from .__libc__ import getifaddrs, IFF_BROADCAST
import ipaddress
import socket
import os
import struct

SYS_TYPE_ETHERNET = 1
SYS_TYPE_LOOPBACK = 772

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
    '''
    This class hosts an Interface address of either IPv4, IPv6 or Link (mac address) family
    '''
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
    '''
    Interface class, either physical or virtual one
    '''
    _address_cache = None

    def __init__(self,device):
        '''
        Creates an Interface object from a given device name, ie: Interface("eth0")
        Not pretended to be public API
        '''
        self.name = device
        self.device_path = "/sys/class/net/"+device

    def interfaces():
        '''
        Static method that returns a list of current available interfaces
        '''
        tmp=[]
        for dev in os.listdir("/sys/class/net"):
            tmp.append(Interface(dev))

        return tmp

    def update():
        '''
        Static method that updates interface addresses. Usually, there is no need to call it.
        '''
        Interface._address_cache = getifaddrs()

    def _check_update():
        if (not Interface._address_cache):
            Interface.update()

    def addresses(self):
        '''
        Returns a list of addresses
        '''
        Interface._check_update()
        if self.name in Interface._address_cache:
            tmp=[]
            for ifa in Interface._address_cache[self.name]:
                i = IFAddress(ifa["family"],ifa["flags"],ifa["address"],ifa.get("netmask"),ifa.get("broadcast"))
                tmp.append(i)

            return tmp

        else:
            return []

    def _read_sys(self,node):
        f=open(self.device_path+"/"+node,"rt")
        line = f.readline().strip()
        f.close()

        return line

    def get_carrier(self):
        '''
        Gets carrier status (device connected to medium)
        '''
        try:
            line = self._read_sys("carrier")
            if(line=="1"):
                return True
            else:
                return False
        except:
            return False

    def get_type(self):
        '''
        Gets interface type, usually SYS_TYPE_ETHERNET or SYS_TYPE_LOOPBACK
        see if_arp.h for more values
        '''
        line = self._read_sys("type")
        return int(line)

    def get_mtu(self):
        '''
        Gets interface MTU
        '''
        line = self._read_sys("mtu")
        return int(line)

def get_ip_from_host(host):
    '''
    Resolves name from host. If it fails, it returns None
    '''
    try:
        return ipaddress.ip_address(socket.gethostbyname(host))
    except Exception:
        return None

def is_ip_in_range(ip,ip_network):
    '''
    Checks whether an ip is a child of a certain network.
    Returns True or False.
    ex:
        is_ip_in_range("10.0.0.160","10.0.0.128/25")
    '''
    #ip_network ex: "10.0.0.128/24"
    try:
        ip=ipaddress.ip_address(ip)
        return ip in list(ipaddress.ip_network(ip_network).hosts())
    except Exception:
        return False

def get_network_ip(ip,netmask):
    '''
    Computes network ip from a given ip host and a netmask
    '''
    net = ipaddress.ip_network(ip+"/"+netmask,strict=False)
    return net.network_address

def get_net_size(netmask):
    '''
    Calculates bitmask from netmask
    ie:
        get_net_size("255.255.255.0") -> 24
    '''
    netmask=netmask.split(".")
    binary_str = ''
    for octet in netmask:
        binary_str += bin(int(octet))[2:].zfill(8)
    return str(len(binary_str.rstrip('0')))

#def get_net_size

def get_default_gateway():
    '''
    Returns default gateway.
    '''
    with open("/proc/net/route") as fh:
        count=0
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue

            return count,socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

    return None
