"""
Unit Test For check_nrpe check_disk local & check_disk remote
"""
import subprocess
import re
import sys


gitLab = "deploy/gitlab"
with open(gitLab,"r") as file:
    for line in file.readlines():
        if "NAGIOS_DIR" in line:
            libexec = line.split("=")[-1].strip()+"/libexec/"
            break
failedCount = 0


def runCommand(command):
    '''
    Run shell commands
    '''
    stdOutput = ''
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = process.stdout.readline()
        if not line:
            break
        stdOutput += str(line)
    if process.wait() != 0:
        return False,str(stdOutput).strip()
    else:
        return True,str(stdOutput).strip()


def checkNrpe(hostIP):
    global failedCount
    command = "{0}check_nrpe -H {1} -t 60".format(libexec,hostIP)
    result,output = runCommand(command)
    if not result:
        print (output,"\nNRPE Check FAILED")
        failedCount +=1


def checkDiks(mode,hostIP):
    global failedCount
    status = ["DISK WARNING","DISK CRITICAL","DISK OK"]
    if mode == "local":
        command = "{0}check_disk -w 10% -c 5% -p /home".format(libexec)
        commandFormat = "{0}check_disk -w {1} -c {2} -p /home"
    if mode == "remote":
        command = "{0}check_nrpe -H {1} -t 60 -c check_disk -a '10%' '5%' '/home/wcdma_cb'".format(libexec,hostIP)
        commandFormat = "{0}check_nrpe -H %s -t 60 -c check_disk -a '{1}' '{2}' '/home/wcdma_cb'" % hostIP
    result,output = runCommand(command)
    if "DISK WARNING" in output or "DISK CRITICAL" in output or "DISK OK" in output:
        freeSpace = int(re.findall(r"\d+ MB",output)[0].split()[0])
        for warn,critical in [(freeSpace+500,freeSpace-500),(freeSpace+1000,freeSpace+500),(freeSpace-500,freeSpace-1000)]:
            for state in status:
                command = commandFormat.format(libexec,warn,critical)
                result,output = runCommand(command)
                if not state in output:
                    print ("{0} Check FAILED".format(state))
                    failedCount +=1
                    del status[status.index(state)]
                    break
                else:
                    del status[status.index(state)]
                    break
    else:
        print ("{0} Disk Check FAILED".format(mode))
        failedCount += 1


if __name__ == "__main__":
    hostIP = "10.159.69.46"
    checkNrpe(hostIP)
    checkDiks("local",hostIP)
    checkDiks("remote",hostIP)
    if failedCount > 0:
        print("NRPE Local DISK Remote DISK Test FAILED")
        sys.exit(1)
    else:
        print("NRPE Local DISK Remote DISK Test PASS")
