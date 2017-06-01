#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Nokia Siemens Networks. All rights reserved.
#
#

"""The script is for checking whether a dir is mounted."""

__author__ = [
    '"Mason" <wei-mason.su@nokia.com>'
]

import logging
import subprocess
import sys
import os

from check_disk_rw import CheckDiskRW

dir_name_to_remote_address_mapping = {'/bts_gmps_hz' : {'path' : 'hzlinn10.china.nsn-net.net:/vol/hzlinn10_bin/build/bts_gmps_hz', 'username' : 'tdlteman', 'other_op' : 'rw'}, 
                                                   '/lteCB' : {'path' : 'hzlinn10.china.nsn-net.net:/vol/hzlinn10_bin/lteCB', 'username' : 'tdlteman', 'other_op' : 'rw'},
                                                   '/lteRel' : {'path' : 'hzlinn10.china.nsn-net.net:/vol/hzlinn10_grp/ee_groups_lin/lteRel', 'username' : 'tdlteman', 'other_op' : 'rw'},
                                                   '/mnt/TDD_release' : {'path' : '//10.159.194.62/eefs00013658/TDD_release', 'username' : 'tdlteman', 'other_op' : 'rw'},
                                                   '/build/ltesdkroot' : {'path' : 'hzchon11.china.nsn-net.net:/vol/hzchon11_ltesdk/ltesdkroot/ltesdkroot', 'username' : 'tdlteman', 'other_op' : 'r'},
                                                   '/build/home' : {'path' : 'hzchon10.china.nsn-net.net:/vol/hzchon10_bin/build/build', 'username' : 'tdlteman', 'other_op' : 'rw'},
                                                   '/mnt/TDD_release/FSMr3_trunk_package' : {'path' : '//10.159.194.62/eefs00013658/TDD_release', 'username' : 'tdlteman', 'other_op' : 'rw'},
                                                   '/uicascm' : {'path' : 'bechon60.china.nsn-net.net:/vol/bechon60_rnd/uicascm'},
                                                   '/build' : {'path' : 'belinn60.china.nsn-net.net:/vol/belinn60_bin/build'},
                                                   '/tmp_opt' : {'path' : 'belinn60.china.nsn-net.net:/vol/belinn60_bin/linsee'},
                                                   '/home/uicaci' : {'path' : 'belinn60.china.nsn-net.net:/vol/belinn60_home/home/uicaci'}
                                                   } 

username_to_password_path_mapping = {'tdlteman' : '~/.password/.tdlteman_passsword'}

class CheckMountedDir():
    def __init__(self, dir_name):
        self.dir_name = dir_name
        
    def check(self):
        if self.dir_name in dir_name_to_remote_address_mapping:
            check_statement = 'df -h ' + self.dir_name 
        
            check_statement_output = self.system_cmd(check_statement, return_output=True)
            check_result = self.check_output(check_statement_output,
                                             dir_name_to_remote_address_mapping[self.dir_name]['path'])
        else:
            print('unspported dir name :', self.dir_name)
            check_result = 1
        
        return check_result
    
    def check_output(self, check_statement_output, remote_address):
        output_list = check_statement_output.split('\n')
        
        check_result = 0
        
        if 0 == check_result and False == (1 <= len(output_list) and 0 == output_list[0].find('Filesystem')):
            check_result = 1
            
        if 0 == check_result and False == (2 <= len(output_list) and output_list[1] == remote_address):
            check_result = 1
        
        return check_result
    
    def system_cmd(self, command, die_on_fail=False, show_output=False, return_output=False):
        """
            executes commands
        """
        logging.debug("Executing: %s", command)
        ### guess that try statement is not needed, returncode check is enough (and not everything is catched by OSError and ValueError)
        try:
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (OSError, ValueError) as err:
            logging.info(traceback.format_exc())
            logging.error("Unable to execute %s", command)
            logging.debug(err)
            sys.exit(1)
        out, err = proc.communicate()
        out, err = out.decode('utf-8'), err.decode('utf-8')
        logging.debug("Returncode: %s", proc.returncode)
    
        if proc.returncode:
            logging.error("Error while executing %s", command)
            logging.error(err)
            if die_on_fail:
                raise KnifeError(reason="Failed on executing command.")
        else:
            if show_output:
                if out:
                    logging.info(out)
                if err:
                    logging.info(err)
   
        if return_output:
            return out
        else:
            return proc.returncode

def main():
    (root_path, file_name) = os.path.split(os.path.abspath(__file__))
    check_result_for_all = 0
    dir_argument = sys.argv[1]
    dir_list = dir_argument.split(',')
    
    for dir_name in dir_list:
        check_mounted_dir = CheckMountedDir(dir_name)
        check_result = check_mounted_dir.check()
        
        if 0 != check_result:
            print('dir ', dir_name, ' : check mount failed')
            check_result_for_all = 1
        elif 'rw' == dir_name_to_remote_address_mapping[dir_name]['other_op']:
            username = dir_name_to_remote_address_mapping[dir_name]['username']
            password_file_path =  username_to_password_path_mapping[username]
            check_rw_command = root_path + "/run_as_another_user.sh " + username  + " " + password_file_path  + " 'python " + root_path + "/check_disk_rw.py " + dir_name + " > /dev/null'"
            if 0 != check_mounted_dir.system_cmd(check_rw_command):
                print('dir ', dir_name, ' : check read and write failed')
                check_result_for_all = 1
        else:
            check_r_command = 'ls ' + dir_name
            if 0 != check_mounted_dir.system_cmd(check_r_command):
                print('dir ', dir_name, ' : check read failed')
                check_result_for_all = 1
    
    return check_result_for_all
        
if __name__ == '__main__':
    result = main()
    print('check_mounted_dir result :', result)
    exit(result)
    
