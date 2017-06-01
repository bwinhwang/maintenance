#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Nokia Siemens Networks. All rights reserved.
#
#

"""The unit test is for check_disk_rw."""

__author__ = [
    '"Mason" <wei-mason.su@nokia.com>'
]

import unittest
from unittest.mock import MagicMock
import os
import glob
import sys

(root_path, file_name) = os.path.split(os.path.abspath(__file__))
(root_path, file_name) = os.path.split(root_path)
(root_path, file_name) = os.path.split(root_path)
sys.path.append(root_path + "/Nagios/libexec/")
from check_disk_rw import CheckDiskRW

class TestCheckDiskRW(unittest.TestCase):
    rootpath = os.path.split(os.path.abspath(__file__))
    def tearDown(self):
        tempFileList = glob.glob('MB_check_rw*')
        for file_index in range(len(tempFileList)):
            os.remove(tempFileList[file_index])
        
    def test_read_fine_and_write_fine(self):
        check_disk_rw = CheckDiskRW('./')
        self.assertEqual(check_disk_rw.check(), 0)
        
    def test_read_wrong_and_write_fine(self):
        check_disk_rw = CheckDiskRW('./')
        exists_fun_obj = os.path.exists
        os.path.exists = MagicMock(return_value=False)
        self.assertEqual(check_disk_rw.check(), 1)
        os.path.exists = exists_fun_obj
          
    def test_read_fine_and_write_wrong(self):
        check_disk_rw = CheckDiskRW('./')
        remove_fun_obj = os.remove 
        os.remove = MagicMock(return_value=False)
        self.assertEqual(check_disk_rw.check(), 1)
        os.remove = remove_fun_obj
    
if __name__ == "__main__":
    unittest.main()
    
