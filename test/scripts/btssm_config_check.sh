#!/bin/sh

echo "btssm check commands"
echo $PWD
echo "get btssm servers:"
NRPE="Nagios/libexec/check_nrpe"
#BTSSM_CONFIG_DIR="Nagios/etc/btssm"

BTSSM_CONFIG_DIR="../../Nagios/etc/btssm"
BTSSM_SERVERS_DIR="${BTSSM_CONFIG_DIR}/servers"
BTSSM_LINSEE_FILE="${BTSSM_SERVERS_DIR}/linsee"
BTSSM_EECLOUD_FILE="${BTSSM_SERVERS_DIR}/eecloud"
BTSSM_SERVER_FILES=`ls ${BTSSM_CONFIG_DIR}/servers`
FCT_PTR=""


function parse_check_load()
{
	local FILE=$1
	local PORT=$2
	local ADDR=`grep address ${BTSSM_SERVERS_DIR}/$FILE | awk '{ print $2}'`	
	local LINES=`grep check_load ${BTSSM_SERVERS_DIR}/$FILE | grep -v \# | awk '{ print $2}'`
	
#	echo -e "\tFILE:${FILE} ADDR:${ADDR} PORT:${PORT}"
	for LINE in $LINES
	do
#		echo "$LINE"
		ARG=`echo $LINE | awk -F $ '{ print $2}'`
		echo  "$ARG"
#		ARG1= echo $ARG | awk -F ! ' { print $1}'
#		ARG2= echo $ARG | awk -F ! ' { print $2}'
#		ARG3= echo $ARG | awk -F ! ' { print $3}'
#		ARG4= echo $ARG | awk -F ! ' { print $4}'
#		echo -e "\t\tParse: ${ARG1} ${ARG2} ${ARG3} ${ARG4}"	
#	${NRPE} -p ${PORT} -H ${ADDR} -u -t 15 -c ${CMD} -a -h > /dev/null 
	done
}

function parse_check_zombie_proc()
{
	echo "zombie"
}

function parse_check_total_proc()
{
	echo "proc"
}

function parse_check_mem()
{
	echo "mem"
}

function parse_check_disk()
{
	echo "disk"
}

function parse_check_users()
{
	echo "users"
}

function check_cmd()
{
#	echo -e "\tCMD:$1"
	case "$1" in
		check_load ) 	parse_check_load $2 $3; 		FCT_PTR="parse_check_load";;
#		check_zombie_procs ) parse_check_zombie_proc $2; 	FCT_PTR="parse_check_zombie_proc";;
#		check_total_procs ) parse_check_total_proc $2;	FCT_PTR="parse_check_total_proc";;
#		check_mem )	parse_check_mem $2;		FCT_PTR="parse_check_mem";;
#		check_disk )	parse_check_disk $2;		FCT_PTR="parse_check_disk";;
#		check_users )	parse_check_users $2;		FCT_PTR="parse_check_users";;
#		* )		
#			echo "$1 : NOT support cmd"
#			return
	esac	
}

function check_cmds()
{
	local ADDR=${1}
	local CMD=${2}
	local PORT=${3}
	echo -e "\tADDR:${ADDR} CMD:${CMD} PORT:${PORT}"
	${NRPE} -p ${PORT} -H ${ADDR} -u -t 15 -c ${CMD} -a -h > /dev/null 
	echo -e "\t\tRET:$?"
}


for FILE in `cat $BTSSM_LINSEE_FILE`
do 
#	echo $FILE
#	ADDR=`grep address ${BTSSM_SERVERS_DIR}/$FILE | awk '{ print $2}'`	
	CMDS=`grep check_nrpe ${BTSSM_SERVERS_DIR}/$FILE | grep -v \# | awk -F ! '{ print $2}' | sort -u`
	for CMD in ${CMDS}
	do
#		check_cmds $ADDR $CMD 8080 
		check_cmd ${CMD} ${FILE} 8080
	done
done


#for FILE in `cat $BTSSM_EECLOUD_FILE`
#do 
#	echo $FILE
#	ADDR=`grep address ${BTSSM_SERVERS_DIR}/$FILE | awk '{ print $2}'`
#	CMDS=`grep check_nrpe ${BTSSM_SERVERS_DIR}/$FILE | grep -v \#  | awk -F ! '{ print $2}' | sort -u`
#	for CMD in ${CMDS}
#	do
#		check_cmds $ADDR $CMD 8080
#		check_cmd ${CMD} ${FILE} 8080
#	done
#done







