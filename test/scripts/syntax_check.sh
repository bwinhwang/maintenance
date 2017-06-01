export PATH=/home/nagiosadmin/tools/python2.7/python-2.7.9/bin:$PATH
cd $GIT_PROJECT/test/testcases
basepath=`pwd`
pysys.py run | tee -a $basepath/tmp.log
if grep -q "THERE WERE NO NON PASSES" $basepath/tmp.log; then
	rm -fr $basepath/tmp.log
	exit 0
else
	rm -fr $basepath/tmp.log
	exit 1
fi

