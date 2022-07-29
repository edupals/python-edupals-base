import socket
from ctypes import (
    Structure, Union, POINTER,
    pointer, get_errno, cast,
    c_ushort, c_byte, c_void_p, c_char_p, c_uint, c_int, c_uint16, c_uint32
)
import ctypes.util
import ctypes

IFF_UP = 0x01
IFF_BROADCAST = 0x02
IFF_DEBUG = 0x03
IFF_LOOPBACK = 0x04
IFF_POINTOPOINT = 0x05
IFF_NOTRAILERS = 0x06
IFF_RUNNING = 0x07
IFF_NOARP = 0x08
IFF_PROMI = 0x09
IFF_ALLMULTI = 0x0a
IFF_MASTER = 0x0b
IFF_SLAVE = 0x0c
IFF_MULTICAS = 0x0d
IFF_PORTSEL = 0x0e
IFF_AUTOMEDIA = 0x0f
IFF_DYNAMIC = 0x10

class struct_sockaddr(Structure):
     _fields_ = [
        ('sa_family', c_ushort),
        ('sa_data', c_byte * 14),]

class struct_sockaddr_in(Structure):
    _fields_ = [
        ('sin_family', c_ushort),
        ('sin_port', c_uint16),
        ('sin_addr', c_byte * 4)]

class struct_sockaddr_in6(Structure):
    _fields_ = [
        ('sin6_family', c_ushort),
        ('sin6_port', c_uint16),
        ('sin6_flowinfo', c_uint32),
        ('sin6_addr', c_byte * 16),
        ('sin6_scope_id', c_uint32)]

class struct_sockaddr_ll(Structure):
    _fields_ = [
        ('sll_family', c_ushort),
        ('sll_protocol', c_ushort),
        ('sll_ifindex', c_int),
        ('sll_hatype', c_ushort),
        ('sll_pkttype', c_byte),
        ('sll_halen', c_byte),
        ('sll_addr', c_byte * 8)]

class union_ifa_ifu(Union):
    _fields_ = [
        ('ifu_broadaddr', POINTER(struct_sockaddr)),
        ('ifu_dstaddr', POINTER(struct_sockaddr)),]

class struct_ifaddrs(Structure):
    pass

struct_ifaddrs._fields_ = [
    ('ifa_next', POINTER(struct_ifaddrs)),
    ('ifa_name', c_char_p),
    ('ifa_flags', c_uint),
    ('ifa_addr', POINTER(struct_sockaddr)),
    ('ifa_netmask', POINTER(struct_sockaddr)),
    ('ifa_ifu', union_ifa_ifu),
    ('ifa_data', c_void_p),]

libc = ctypes.CDLL(ctypes.util.find_library('c'))

def ifap_iter(ifap):
    ifa = ifap.contents
    while True:
        yield ifa
        if not ifa.ifa_next:
            break
        ifa = ifa.ifa_next.contents

def getifaddrs():
    ifap = POINTER(struct_ifaddrs)()
    status = libc.getifaddrs(pointer(ifap))
    result={}

    for ifa in ifap_iter(ifap):
        if(ifa.ifa_addr):
            name=ifa.ifa_name.decode("ascii")
            tmp={}
            tmp["family"]=ifa.ifa_addr.contents.sa_family
            flags = ifa.ifa_flags & 0xffff
            tmp["flags"]= flags

            if (ifa.ifa_addr.contents.sa_family == socket.AF_INET):
                sa = cast(pointer(ifa.ifa_addr.contents), POINTER(struct_sockaddr_in)).contents
                tmp["address"] = socket.inet_ntop(sa.sin_family, sa.sin_addr)

                if (ifa.ifa_netmask):
                    sm = cast(pointer(ifa.ifa_netmask.contents), POINTER(struct_sockaddr_in)).contents
                    tmp["netmask"] = socket.inet_ntop(sa.sin_family, sm.sin_addr)

                if ((flags & IFF_BROADCAST != 0) and ifa.ifa_ifu.ifu_broadaddr):
                    sb = cast(pointer(ifa.ifa_ifu.ifu_broadaddr.contents), POINTER(struct_sockaddr_in)).contents
                    tmp["broadcast"] = socket.inet_ntop(sa.sin_family, sb.sin_addr)
            elif (ifa.ifa_addr.contents.sa_family == socket.AF_INET6):
                sa = cast(pointer(ifa.ifa_addr.contents), POINTER(struct_sockaddr_in6)).contents
                tmp["address"] = socket.inet_ntop(sa.sin6_family, sa.sin6_addr)

                if (ifa.ifa_netmask):
                    sm = cast(pointer(ifa.ifa_netmask.contents), POINTER(struct_sockaddr_in6)).contents
                    tmp["netmask"] = socket.inet_ntop(sa.sin6_family, sm.sin6_addr)

                if ((flags & IFF_BROADCAST != 0) and ifa.ifa_ifu.ifu_broadaddr):
                    sb = cast(pointer(ifa.ifa_ifu.ifu_broadaddr.contents), POINTER(struct_sockaddr_in6)).contents
                    tmp["broadcast"] = socket.inet_ntop(sa.sin_family, sb.sin6_addr)

            elif (ifa.ifa_addr.contents.sa_family == socket.AF_PACKET):
                sa = cast(pointer(ifa.ifa_addr.contents), POINTER(struct_sockaddr_ll)).contents
                mac=[]

                #assuming MAC-48 address
                for n in range(6):
                    mac.append(sa.sll_addr[n] & 0xff)
                tmp["address"] = mac

            if not name in result:
                result[name]=[]
            result[name].append(tmp)
            #print(tmp)

    libc.freeifaddrs(ifap)

    return result
