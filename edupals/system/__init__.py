import os
import sys

class Mount:
    def __init__(self,data):
        self.device = data[0]
        self.mount_point = data[1]
        self.fs_type = data[2]
        self.ro = data[3]
        self.dummy = data[4]

def _read_line_(path):
    f=open(path,"r")
    data=f.readline().strip()
    f.close()
    return data

def version():
    return _read_line_("/proc/version")

def uptime():
    data = _read_line_("/proc/uptime")
    tmp = data.split()

    return float(tmp[0])

def cmdline():
    return _read_line_("/proc/cmdline")

def modules():
    f = open("/proc/modules","r")
    lines = f.readlines()
    f.close()

    ret=[]
    for line in lines:
        tmp = line.split()
        ret.append(tmp[0])

    return ret

def _is_pid_(pid):
    for c in pid:
        code = ord(c)
        if (code < ord('0') or code > ord('9')):
            return False

    return True

def pids():
    tmp=[]
    for f in os.listdir("/proc"):
        if (_is_pid_(f)):
            tmp.append(int(f))

    return tmp

def mounts():
    f = open("/proc/mounts","r")
    lines = f.readlines()
    f.close()

    ret=[]
    for line in lines:
        tmp = line.split()
        ret.append(Mount(tmp))

    return ret
