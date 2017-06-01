#!/bin/sh

function help()
{
	echo "./check_jenkins_process pathname"
}

if [ $# != 1 ]
then
	help
fi	

RET=`ps ax | grep jenkins.war | grep -v grep | grep $1 1>/dev/null 2>/dev/null`

if [ 0 -ne $RET ]
then
    echo "ERROR"
    exit 2
else
    echo "OK"
    exit 0
fi

