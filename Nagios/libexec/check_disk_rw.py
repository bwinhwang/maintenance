#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Nokia Siemens Networks. All rights reserved.
#
#

"""The script implements the check that whether the disk has read and write permission."""

__author__ = [
    '"Mason" <wei-mason.su@nokia.com>'
]
  
import tempfile
import os
import sys
   
class CheckDiskRW:
    def __init__(self, dir_name):
        self.dir_name = dir_name
    
    def check(self):
        check_result = 0
        tmpfile = tempfile.NamedTemporaryFile(prefix='MB_check_rw', dir=self.dir_name, delete=False)
        
        tmp_file_path = tmpfile.name
        tmpfile.close()
        if False == os.path.exists(tmp_file_path):
            print('CheckDiskRW:check tmp file', tmp_file_path, ' does not exist')
            check_result = 1
        else:
            os.remove(tmp_file_path)
            
        if 0 == check_result and True == os.path.exists(tmp_file_path):
            print('CheckDiskRW:check tmp file', tmp_file_path, ' can not be deleted')
            check_result = 1
        
        return check_result

def main():
    check_disk_rw = CheckDiskRW(sys.argv[1])
    return check_disk_rw.check()

if __name__ == '__main__':
    result = main()
    print('check_disk_rw result :', result)
    exit(result) 

