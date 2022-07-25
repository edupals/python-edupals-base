from .__libc__ import getifaddrs, IFF_BROADCAST
import ipaddress
import socket
import os

class MacAddress:
    address = [0x00,0x00,0x00,0x00,0x00,0x00]

    def __init__(self,address):
        self.address = address

    def __str__(self):
        tmp=""
        for octet in self.address:
            tmp+="{:02X}:".format(octet)
        tmp=tmp[:-1]
        return tmp

class IFAddress:

    family = 0
    flags = 0
    address = None
    netmask = None
    broadcast = None

    def __init__(self,family,flags,address,netmask,broadcast):
        self.family = family
        self.flags = flags
        if family==socket.AF_INET:
            self.address = ipaddress.IPv4Address(address)
            if (netmask):
                self.netmask = ipaddress.IPv4Address(netmask)
            if (broadcast):
                self.broadcast = ipaddress.IPv4Address(broadcast)

        elif family==socket.AF_INET6:
            self.address = ipaddress.IPv6Address(address)
            if (netmask):
                self.netmask = ipaddress.IPv6Address(netmask)
            if (broadcast):
                self.broadcast = ipaddress.IPv6Address(broadcast)

        elif family==socket.AF_PACKET:
            self.address = MacAddress(address)

    def __str__(self):
        if (self.family == socket.AF_INET or self.family == socket.AF_INET6):
            return "{0}/{1}/{2}".format(self.address,self.netmask,self.broadcast)
        else:
            return str(self.address)

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
        Interface._address_cache = getifaddrs()

    def _check_update():
        if (not Interface._address_cache):
            Interface.update()

    def addresses(self):
        Interface._check_update()
        if self.name in Interface._address_cache:
            tmp=[]
            for ifa in Interface._address_cache[self.name]:
                i = IFAddress(ifa["family"],ifa["flags"],ifa["address"],ifa.get("netmask"),ifa.get("broadcast"))
                tmp.append(i)

            return tmp

        else:
            return []

    def carrier(self):
        try:
            f=open(self.device_path+"/carrier","rt")
            line = f.readline().strip()
            f.close()

            if(line=="1"):
                return True
            else:
                return False
        except:
            return False

def get_ip_from_host(host):
    '''
    Resolves name from host. If it fails, it returns None
    '''
    try:
        return ipaddress.ip_address(socket.gethostbyname(host))
    except Exception:
        return None
