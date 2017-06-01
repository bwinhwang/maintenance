#!/bin/sh
function usage()
{
  echo usage: $0 ENV git_branch
  exit 1
}

if [ $# -ne 2 ]
then 
  usage
elif [[ ! "production|test|gitlab" =~ "$1" ]]
then
  echo only production or test env available
  exit 1
fi

ENV=$1
BRANCH=$2
source $(dirname $0)/$ENV

function check_out_workspace()
{
  if [ "$BRANCH" == "gitlab" ]
  then 
    return 0
  fi

  if [ ! -d "$GIT_PROJECT"/.git ] 
  then
    rm -fr $GIT_PROJECT
    git clone ${REPOS} $GIT_PROJECT
    git reset --hard
  else
    cd $GIT_PROJECT
    git reset --hard
    git fetch origin
  fi
  git checkout $BRANCH 
  git pull || :
}

function install_httpd()
{
  rm -fr ${NAGIOS_HTTPD} && mkdir -p ${NAGIOS_HTTPD}
  cp -r ${NAGIOS_APACHE_SRC}/* ${NAGIOS_HTTPD}
}

function deploy_new_view()
{
  rm -fr ${NAGIOS_DIR}/share $GIT_PROJECT/src/${NAGIOS_VIEW_DIR}
  unzip ${NAGIOS_VIEW_SRC} -d $GIT_PROJECT/src/
  if [ -d $GIT_PROJECT/share ]; then
	cp -r $GIT_PROJECT/share ${NAGIOS_DIR}/share
  else
	cp -r $GIT_PROJECT/src/${NAGIOS_VIEW_DIR} ${NAGIOS_DIR}/share
  fi
}

function install_nagios()
{
  mkdir -p $GIT_PROJECT/src
  cp $NAGIOS_SRC  $GIT_PROJECT/src
	cd $GIT_PROJECT/src
	tar -xzvf $NAGIOS_VER && cd nagios
	./configure --prefix=${NAGIOS_DIR} --with-nagios-user=${NAGIOS_USER} --with-nagios-group=${NAGIOS_GROUP}\
	 --with-init-dir=${NAGIOS_DIR}/init --with-httpd-conf=${NAGIOS_HTTPD}
	make all -j16 && make install
}

function install_nagios_plugin()
{
 cp $NAGIOS_PLUGINS_SRC $GIT_PROJECT/src && cd $GIT_PROJECT/src
 tar -xzvf $NAGIOS_PLUGINS_VER && cd $NAGIOS_PLUGINS_VER_DIR 
 ./configure --prefix=${NAGIOS_DIR} --with-nagios-user=${NAGIOS_USER} --with-nagios-group=${NAGIOS_GROUP} && make -j 4 && make install
}

function install_nrpe_plugin()
{
 cp $NRPE_SRC $GIT_PROJECT/src && cd $GIT_PROJECT/src 
 tar -xzvf ${NRPE_VER} && cd $NRPE_VER_DIR 
 ./configure --prefix="${NAGIOS_DIR}" --enable-command-args  --with-nrpe-user="${NAGIOS_USER}" \
   --with-nrpe-group="${NAGIOS_GROUP}" --with-nagios-user="${NAGIOS_USER}" --with-nagios-group="${NAGIOS_GROUP}";
 make && make install
}

function install_pnp4nagios()
{
  cp ${PNP4NAGIOS_SRC} $GIT_PROJECT/src && cd $GIT_PROJECT/src
  tar -xzvf ${PNP4NAGIOS_VER} && cd ${PNP4NAGIOS_VER_DIR}
  ./configure --prefix=${PNP4NAGIOS_PATH} --with-httpd-conf=${NAGIOS_HTTPD}/conf \
    --with-nagios-user=${NAGIOS_USER} --with-nagios-group=${NAGIOS_GROUP} \
    --with-nrpe-user=${NAGIOS_USER} --with-nrpe-group=${NAGIOS_GROUP} ;\
    make all || exit 1
    make install || exit 1
    make install-webconf || exit 1
    make install-config || exit 1
  sed -i "s#pid_file=/var/run/npcd.pid#pid_file=${PNP4NAGIOS_PATH}/etc/npcd.pid#g" ${PNP4NAGIOS_PATH}/etc/npcd.cfg
  for file in `find ${PNP4NAGIOS_PATH}/etc/ -name "*.cfg-sample"`
  do
	  new_file=`echo $file | sed 's#-sample##g'`
	  mv $file $new_file
  done
  rm -fr ${PNP4NAGIOS_PATH}/share/install.php
}

function pnp4nagios_patch()
{
  if ! grep -q '# Bulk / NPCD mode' ${NAGIOS_DIR}/etc/nagios.cfg
  then
    sed '/# Bulk \/ NPCD mode/, /# Module mode/p' ${PNP4NAGIOS_PATH}/etc/nagios.cfg -n >> ${NAGIOS_DIR}/etc/nagios.cfg
  fi
  
  if ! grep -q 'Alias /pnp4nagios' ${NAGIOS_HTTPD}/conf/httpd.conf
  then
    sed  "s#/usr/local/nagios/etc/htpasswd.users#${NAGIOS_DIR}/etc/htpasswd.users#g" ${NAGIOS_HTTPD}/conf/pnp4nagios.conf >> ${NAGIOS_HTTPD}/conf/httpd.conf
  fi

  sed -i "s#PNP4_PATH_VARIABLE#${PNP4NAGIOS_PATH}#g" ${NAGIOS_HTTPD}/conf/httpd.conf
}

function fix_path()
{
  for file in `find ${NAGIOS_DIR} -name "*.cfg"`
  do
    sed -i "s#/var/fpwork/#${NAGIOS_DIR}/#g" $file
  done
}

function start_services()
{
  httpd_pid=$(ps -ef |grep ${NAGIOS_HTTPD}/bin/httpd |grep -v grep| awk '{print $2}') 
  nagios_pid=$(ps -ef |grep ${NAGIOS_DIR}/bin/nagios |grep -v grep| awk '{print $2}') 
  npcd_pid=$(ps -ef |grep ${PNP4NAGIOS_PATH}/bin/npcd |grep -v grep| awk '{print $2}') 
  if [ -n "$httpd_pid$nagios_pid$npcd_pid" ]
  then
    kill -9 $httpd_pid $nagios_pid $npcd_pid
  fi
  mkdir -p ${NAGIOS_DIR}/var/rw/
  ${NAGIOS_DIR}/bin/nagios -d ${NAGIOS_DIR}/etc/nagios.cfg || exit 1
  ${NAGIOS_HTTPD}/bin/httpd -f ${NAGIOS_HTTPD}/conf/httpd.conf || exit 1
  ${PNP4NAGIOS_PATH}/bin/npcd -f ${PNP4NAGIOS_PATH}/etc/npcd.cfg -d
}

function apply_nagios_patch()
{
  rm -fr ${NAGIOS_HTTPD}/conf
  cp -rf ${GIT_PROJECT}/Apache_conf ${NAGIOS_HTTPD}/conf 
  rm -fr ${NAGIOS_DIR}/etc
  cp -r ${GIT_PROJECT}/Nagios/etc ${NAGIOS_DIR}/etc
  cp -r ${GIT_PROJECT}/Nagios/libexec/* ${NAGIOS_DIR}/libexec
  for file in `find ${NAGIOS_HTTPD}/conf ${NAGIOS_DIR}/etc/ -type f`
  do
    sed -i "s#APACHE_PATH_VARIABLE#${NAGIOS_HTTPD}#g" $file
    sed -i "s#NAGIOS_PATH_VARIABLE#${NAGIOS_DIR}#g" $file
    sed -i "s#PNP4_PATH_VARIABLE#${PNP4NAGIOS_PATH}#g" $file
  done
  sed -i "s#HTTP_PORT#$HTTP_PORT#g" ${NAGIOS_HTTPD}/conf/httpd.conf
  if [[ -e "${NAGIOS_DIR}/libexec/mail.py" && "$ENV" != "production" ]]
  then
    sed -i '/self.send_mail()/d' ${NAGIOS_DIR}/libexec/mail.py
  fi
}

### main()
check_out_workspace || exit 1
if [ ! -e "${NAGIOS_HTTPD}/bin/httpd" ]
then
  install_httpd || exit 1
fi

if [ ! -e "${NAGIOS_DIR}/bin/nagios" ]
then
  install_nagios || exit 1
fi

if [ ! -e "${NAGIOS_DIR}/libexec/check_http" ]
then 
  install_nagios_plugin || exit 1
fi

if [ ! -e "${NAGIOS_DIR}/bin/nrpe" ]
then 
  install_nrpe_plugin  || exit 1
fi

apply_nagios_patch || exit 1
if [ ! -e "${PNP4NAGIOS_PATH}/libexec/process_perfdata.pl" ]
then
  install_pnp4nagios || exit 1
fi
pnp4nagios_patch || exit 1

${NAGIOS_DIR}/bin/nagios -v ${NAGIOS_DIR}/etc/nagios.cfg || exit 1
${NAGIOS_HTTPD}/bin/httpd -tf ${NAGIOS_HTTPD}/conf/httpd.conf || exit 1
if [ "$BRANCH" != "gitlab"  ]
then
  deploy_new_view
  start_services || exit 1
fi
