#!/bin/bash
root_path=$(dirname $0)
script_path="${root_path}/../../Nagios/libexec"
test_script=${script_path}/check_tools_ver

log_pass(){
    echo "### $1 passed ###"
}

log_fail(){
    echo "### $1 failed ###"
}

assert_eq(){
    assert_ret=$1
    wanted=$2
    test_name=$3
    if [ $assert_ret -eq $wanted ]; then
        log_pass $test_name
        return 0
    else
        log_fail $test_name 
        return 1
    fi
}

assert_ne(){
    assert_ret=$1
    wanted=$2
    test_name=$3
    if [ $assert_ret -ne $wanted ]; then
        log_pass $test_name
        return 0
    else
        log_fail $test_name 
        return 1
    fi
}

create_envfile(){
    envfile=`mktemp /tmp/tmp.XXXXXX`
    envcmd=`mktemp /tmp/tmp.XXXXXX`
    echo "export TEST_ENV=\"1234\"" > $envfile
    echo "echo \$TEST_ENV" > $envcmd 
    chmod a+x $envcmd 
}

clean_envfile(){
    rm -fr $envfile
    rm -fr $envcmd 
}

get_testenv(){
    export gccver=`gcc -dumpversion`
    export errgccver="${gccver}.1.1"
    export pythonver=`python --version 2>&1 | grep Python | awk '{print $2}'`
}

init_env(){
    get_testenv
    create_envfile
}

clean_env(){
    clean_envfile
}

get_ret(){
    if [ $ret -eq 0 ]; then
        echo "*** TOOL CHECK All PASSED ***"
    else
        echo "*** TOOL CHECK FAILED ***"
    fi
}

test_rightver(){
    ${test_script} -t gcc,${gccver}  > /dev/null
    assert_eq $? 0 ${FUNCNAME[@]%main}
}

test_wrongver(){
    ${test_script} -t gcc,${errgccver}  > /dev/null
    assert_eq $? 2 ${FUNCNAME[@]%main}
}

test_wrongcmd(){
    ${test_script} -t notexistcmd,1234  > /dev/null
    assert_eq $? 2  ${FUNCNAME[@]%main}
}

test_toolgroup(){
    ${test_script} -t gcc,${gccver} python,${pythonver}  > /dev/null
    assert_eq $? 0 ${FUNCNAME[@]%main}
}

test_rightver_withenv(){
    ${test_script} -e "source $envfile" -t "$envcmd,1234"  > /dev/null
    assert_eq $? 0 ${FUNCNAME[@]%main}
}

test_wrongver_withenv(){
    ${test_script} -e "source $envfile" -t "$envcmd,4321"  > /dev/null
    assert_eq $? 2 ${FUNCNAME[@]%main}
}

#___main___
ret=0
init_env
test_rightver || ret=1
test_wrongver || ret=1
test_wrongcmd || ret=1
test_toolgroup || ret=1
test_rightver_withenv || ret=1
test_wrongver_withenv || ret=1
clean_env
get_ret
