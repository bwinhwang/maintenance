#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Nokia Siemens Networks. All rights reserved.
#
#

"""The unit test is for check_mounted_dir.py."""

__author__ = [
    '"Mason" <wei-mason.su@nokia.com>'
]

import unittest
from unittest.mock import MagicMock
import unittest.mock as mock
import sys
import os

(root_path, file_name) = os.path.split(os.path.abspath(__file__))
(root_path, file_name) = os.path.split(root_path)
(root_path, file_name) = os.path.split(root_path)
sys.path.append(root_path + "/Nagios/libexec/")

from check_mounted_dir import CheckMountedDir

df_response_bts_gmps_hz = '''Filesystem            Size  Used Avail Use% Mounted on
hzlinn10.china.nsn-net.net:/vol/hzlinn10_bin/build/bts_gmps_hz
                       11T  9.5T  809G  93% /bts_gmps_hz
'''

df_response_lteCB = '''Filesystem            Size  Used Avail Use% Mounted on
hzlinn10.china.nsn-net.net:/vol/hzlinn10_bin/lteCB
                       11T  9.5T  806G  93% /lteCB
'''

df_response_dev = '''Filesystem            Size  Used Avail Use% Mounted on
-                      24G  232K   24G   1% /dev'''

df_response_bts_gmps_hz_with_wrong_remote_address = '''Filesystem            Size  Used Avail Use% Mounted on
-                       11T  9.5T  809G  93% /bts_gmps_hz
'''

df_response_inexistent_dir_bts_gmps_hz = '''df: `/bts_gmps_hz': No such file or directory
df: no file systems processed
'''

class TestCheckMountedDir(unittest.TestCase):
    def test_mounted_dir_bts_gmps_hz(self):
        check_mounted_dir = CheckMountedDir('/bts_gmps_hz')
        check_mounted_dir.system_cmd = MagicMock(return_value=df_response_bts_gmps_hz)
        check_result = check_mounted_dir.check()
        self.assertEqual(check_result, 0)
    
    def test_mounted_dir_lteCB(self):
        check_mounted_dir = CheckMountedDir('/lteCB')
        check_mounted_dir.system_cmd = MagicMock(return_value=df_response_lteCB)
        check_result = check_mounted_dir.check()
        self.assertEqual(check_result, 0)    

    def test_unmounted_dir_dev(self):
        check_mounted_dir = CheckMountedDir('/dev')
        check_mounted_dir.system_cmd = MagicMock(return_value=df_response_dev)
        check_result = check_mounted_dir.check()
        self.assertEqual(check_result, 1)    
    
    def test_mounted_dir_bts_gmps_hz_with_wrong_remote_address(self):
        check_mounted_dir = CheckMountedDir('/bts_gmps_hz')
        check_mounted_dir.system_cmd = MagicMock(return_value=df_response_bts_gmps_hz_with_wrong_remote_address)
        check_result = check_mounted_dir.check()
        self.assertEqual(check_result, 1)        
        
    def test_inexistent_dir(self):
        check_mounted_dir = CheckMountedDir('/bts_gmps_hz')
        check_mounted_dir.system_cmd = MagicMock(return_value=df_response_inexistent_dir_bts_gmps_hz)
        check_result = check_mounted_dir.check()
        self.assertEqual(check_result, 1)
                       
if __name__ == "__main__":
    unittest.main()
