from ._libc_ import getifaddrs

import ipaddress
import socket
import os

class Interface:
    _address_cache = None

    def __init__(self,device):
        self.name = device
        self.device_path = "/sys/class/net/"+device

    def list():
        tmp=[]
        for dev in os.listdir("/sys/class/net"):
            tmp.append(Interface(dev))

        return tmp

    def update():
        print("updating cache...")
        Interface._address_cache = getifaddrs()
        print(Interface._address_cache)

    def _check_update():
        if (not Interface._address_cache):
            Interface.update()

    def addresses(self):
        Interface._check_update()
        if self.name in Interface._address_cache:
            return Interface._address_cache[self.name]
        else:
            return []

def get_ip_from_host(host):
    '''
    Resolves name from host. If it fails, it returns None
    '''
    try:
        return ipaddress.ip_address(socket.gethostbyname(host))
    except Exception:
        return None
