import os
import sys

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
