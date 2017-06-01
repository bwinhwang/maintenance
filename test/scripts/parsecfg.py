import sys
import os

USER1='/var/fpwork/Nagios//libexec'
NAGIOS_DIR = os.environ.get('NAGIOS_DIR','')
if ''==NAGIOS_DIR:
    pass
else:
    USER1=NAGIOS_DIR+'/libexec'

try:
    pro=sys.argv[1]
except IndexError:
    sys.stderr.write("There is no project to verify")
    sys.exit()

project_root = sys.path[0].split('test')[0]+'/Nagios'

files=[]

for root, dirs, fis in os.walk(project_root+'/etc/common'):
    for fn in fis:
        if fn.endswith('.cfg'):
            files.append(root+'/'+fn)

for root, dirs, fis in os.walk(project_root+'/etc/'+pro):
    for fn in fis:
        if fn.endswith('.cfg'):
            files.append(root+'/'+fn)



# file=project_root+'/etc\\tdlte\\tdlte.cfg'

hosts=[]
hostgroups=[]
services=[]
commands=[]
host_flag=False
hostgroup_flag=False
service_flag=False
command_flag=False
map={}

for file in files:
    f=open(file)
    lines = f.readlines()
    for line in lines:
        line = line.replace('{', '')
        line = line.strip();
        if ''==line:
            continue
        if '#'==line[0] or ';'==line[0]:
            continue
        line=' '.join(line.split())
        if 'define host' == line:
            host_flag=True
            continue
        if host_flag:
            if '}' == line:
                host_flag = False
                hosts.append(map)
                map={}
                continue
            if '}' in line:
                line = line.replace('}', '')
                lisp = line.split()
                map[lisp[0]] = ' '.join(lisp[1:]).split(';')[0].strip()
                host_flag = False
                hosts.append(map)
                map={}
                continue
            lisp = line.split()
            map[lisp[0]] = ' '.join(lisp[1:]).split(';')[0].strip()
        if 'define hostgroup' == line:
            hostgroup_flag=True
            continue
        if hostgroup_flag:
            if '}' == line:
                hostgroup_flag = False
                hostgroups.append(map)
                map={}
                continue
            if '}' in line:
                line = line.replace('}', '')
                lisp = line.split()
                map[lisp[0]] = ' '.join(lisp[1:]).split(';')[0].strip()
                hostgroup_flag = False
                hostgroups.append(map)
                map={}
                continue
            lisp = line.split()
            map[lisp[0]] = ' '.join(lisp[1:]).split(';')[0].strip()
        if 'define service' == line:
            service_flag=True
            continue
        if service_flag:
            if '}' == line:
                service_flag = False
                services.append(map)
                map={}
                continue
            if '}' in line:
                line = line.replace('}', '')
                lisp = line.split()
                map[lisp[0]] = ' '.join(lisp[1:]).split(';')[0].strip()
                service_flag = False
                services.append(map)
                map={}
                continue
            lisp = line.split()
            map[lisp[0]] = ' '.join(lisp[1:]).split(';')[0].strip()
        if 'define command' == line:
            command_flag=True
            continue
        if command_flag:
            if '}' == line:
                command_flag = False
                commands.append(map)
                map={}
                continue
            if '}' in line:
                line = line.replace('}', '')
                lisp = line.split()
                map[lisp[0]] = ' '.join(lisp[1:]).split(';')[0].strip()
                command_flag = False
                commands.append(map)
                map={}
                continue
            lisp = line.split()
            map[lisp[0]] = ' '.join(lisp[1:]).split(';')[0].strip()
            
def get_hostnames_by_groupname(groupnames): 
    hostnames=[]
    for groupname in groupnames.split(','):
        found=False
        for group in hostgroups:
            if groupname==group.get('hostgroup_name',''):
                hostnames.extend( group.get('members','').split(','))
                found=True
        if not found:
            sys.stderr.write('There is no groupname '+groupname)
    return hostnames    
 
def get_host_by_host_name(host_name):
    for host in hosts:
        if host_name == host.get('host_name',''):
            return host.get('address','')
    else:
        sys.stderr.write("There is no host_name "+host_name)
        sys.exit()
        
def collect_parameters(command,prefix):
    split_command = command.split('$')[1:]
    comm = '!'.join(split_command)
    split_command = comm.split('!')
    parameters = []
    for str in split_command:
        if prefix in str:
            parameters.append(str.replace(prefix, ''))
    parameters.sort(key=len, reverse=True)
    return parameters

def collect_host_parameters(command):
    pass

def get_command(check_command):
    command = check_command.split('!')[0]
    for comm in commands:
        if command==comm.get('command_name',''):
            return comm.get('command_line','')
    else:
        sys.stderr.write('No command line found with the command name '+check_command)

def replace_parameters_in_command(check_command,use,hostname):
    command = check_command
    service_parameters = collect_parameters(command,'_SERVICE')
    host_parameters = collect_parameters(command,'_HOST')
    for service in services:
        name = service.get('name','')
        if ''==name:
            continue
        if name==use:
            for parameter in service_parameters:
                value = service.get('_'+parameter,'')
                if ''==value:
                    sys.stderr.write("no value found of the parameter "+parameter)
                command = command.replace('_SERVICE'+parameter,value)
            break
    else:
        sys.stderr.write('can not find the service '+use+'\n')
        command=''
    for host in hosts:
        name = host.get('host_name','')
        if ''==name:
            continue
        if name==hostname:
            for parameter in host_parameters:
                value = host.get('_'+parameter,'')
                if ''==value:
                    sys.stderr.write("no value found of the parameter "+parameter)
                command = command.replace('_HOST'+parameter,value)
            break
    else:
        sys.stderr.write('can not find the service '+use+'\n')
        command=''

    command = command.replace('$','')
    return command

for service in services:
    if ''==service.get('check_command',''):
        continue
    check_command=service['check_command']
    host_name = service.get('host_name','')
    hostgroup_name=''
    if ''== host_name:
        hostgroup_name=service.get('hostgroup_name','')
        if ''==hostgroup_name:
            raise Exception('host_name and hostgroup_name at least exist one in service')
    if '$_SERVICE' in check_command:
        use = service.get('use','')
        if ''==use:
            sys.stderr.write('Config Error in service '+service)
            sys.exit()
        check_command=replace_parameters_in_command(check_command,use,host_name)
    if ''==check_command:
        continue
#     if '!' in check_command:
#         check_command = check_command.replace('!',' ')
#         split_check_command = check_command.split()
#         if ''==host_name:
#             for host in get_hostnames_by_groupname(hostgroup_name):
#                 sys.stdout.write(split_check_command[0]+' -H '+get_host_by_host_name(host)+" " +' '.join(split_check_command[1:])+'\n')
#         else:
#             sys.stdout.write(split_check_command[0]+' -H '+get_host_by_host_name(host_name)+" " +' '.join(split_check_command[1:])+'\n')
#     else:
#         if ''==host_name:
#             for host in get_hostnames_by_groupname(hostgroup_name):
#                 sys.stdout.write(check_command+' -H '+get_host_by_host_name(host)+'\n')
#         else:
#             sys.stdout.write(check_command + ' -H '+get_host_by_host_name(host_name)+'\n')
    if '!' in check_command:
        command = get_command(check_command)
        values = check_command.split('!')
        args_num = len( command.split('ARG'))-1
        index = 1
        while(index<=args_num):
            if index>=len(values):
                command = command.replace('ARG'+str(index),'')
            else:
                command = command.replace('ARG'+str(index),values[index])
            index = index+1
        command = command.replace('$USER1$',USER1)
        command = command.replace('$','')
        if ''==host_name:
            for host in get_hostnames_by_groupname(hostgroup_name):
                sys.stdout.write(command.replace('HOSTADDRESS',get_host_by_host_name(host))+'\n')
        else:
            sys.stdout.write(command.replace('HOSTADDRESS',get_host_by_host_name(host_name))+'\n')
    else:
        command = get_command(check_command)
        args_num = len( command.split('ARG'))-1
        index = 1
        while(index<=args_num):
            command = command.replace('ARG'+str(index),'')
            index = index+1
        command = command.replace('$USER1$',USER1)
        command = command.replace('$','')
         
        if ''==host_name:
            for host in get_hostnames_by_groupname(hostgroup_name):
                sys.stdout.write(command.replace('HOSTADDRESS',get_host_by_host_name(host))+'\n')
        else:
            print(command.replace('HOSTADDRESS',get_host_by_host_name(host_name))+'\n')
        
