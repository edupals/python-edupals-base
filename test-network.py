import ipaddress

import edupals.network as network

ifaces = network.Interface.interfaces()

for iface in ifaces:
    print()
    print(iface.name)
    print("virtual:{0}".format(iface.is_virtual()))
    print("wireless:{0}".format(iface.is_wireless()))

    iface_type = iface.get_type()
    print("type:",iface_type)
    if (iface_type==network.SYS_TYPE_ETHERNET):
        print("mtu:",iface.get_mtu())
        print("carrier:",iface.get_carrier())

    for addr in iface.addresses():
        print("* ",addr)
        #print("broadcast:",addr.is_broadcast())

#print(network.get_ip_from_host("rapture"))

print(network.is_ip_in_range("192.168.1.2","192.168.1.0/24"))
print("default interface:{0}".format(network.get_default_interface()))
