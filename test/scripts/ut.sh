#!/bin/sh
set +e
echo ut start

BTSSM_DIR=test/scripts

#${BTSSM_DIR}/btssm_config_check.sh

python test/scripts/test_check_disk_rw.py

python test/scripts/test_check_mounted_dir.py

if python test/scripts/test_nrpe_disk.py
then
    :
else
    echo "*** NRPE DISK CHECK FAILED ***"
    exit 1
fi
if python test/scripts/test_check_load.py
then
    :
else
    echo "*** LOAD CHECK FAILED ***"
    exit 1
fi
sh test/scripts/test_check_tools_ver.sh
