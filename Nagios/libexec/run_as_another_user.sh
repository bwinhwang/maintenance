#!/bin/bash

USER_NAME=$1
PASSWORD_FILE=$2
COMMAND=$3

source $PASSWORD_FILE

expect <<-END
	spawn su ${USER_NAME} -c "${COMMAND}" 
	expect {
		"Password: " {send "${RUN_USER_PASSWORD}\r"}
	}
expect eof
catch wait result
exit [lindex \$result 3]
END

