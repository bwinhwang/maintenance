#!/bin/sh
for file in `find Nagios/ -name "*.cfg"`
do
    sed -i "s#/var/fpwork/#$PWD/#g" $file
done
