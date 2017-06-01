#!/bin/sh
sh deploy/deploy.sh gitlab gitlab
source deploy/gitlab
export GIT_PROJECT=$GIT_PROJECT
export NAGIOS_DIR=$NAGIOS_DIR
sh test/scripts/syntax_check.sh
