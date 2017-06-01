import sys

import test_nrpe_disk as runCommand


libexec = runCommand.libexec
failedCount = 0

def checkLoad():
    global failedCount
    status = ["WARNING","CRITICAL","OK"]
    command = "{0}check_load -w 4,4,4 -c 8,8,8".format(libexec)
    commandFormat = "{0}check_load -w {1} -c {2}"
    result,output = runCommand.runCommand(command)
    if "WARNING" in output or "CRITICAL" in output or "OK" in output:
        for warn,critical in [("0,0,0","100,100,100"),("0,0,0","0,0,0"),("150,150,150","300,300,300")]:
            for state in status:
                command = commandFormat.format(libexec,warn,critical)
                result,output = runCommand.runCommand(command)
                if not state in output:
                    print ("check_load {0} Check FAILED".format(state))
                    failedCount +=1
                    del status[status.index(state)]
                    break
                else:
                    del status[status.index(state)]
                    break
    else:
        print ("Load Check FAILED")
        failedCount += 1

if __name__ == "__main__":
    checkLoad()
    if failedCount > 0:
        print("Load Test FAILED")
        sys.exit(1)
    else:
        print("Load Test PASS")
