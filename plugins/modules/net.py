# Copyright ©️ 2022 Dell Inc. or its subsidiaries.
from __future__ import (absolute_import, division,
                        print_function)
from ansible.module_utils.basic import AnsibleModule
__metaclass__ = type

import os
try:
    import paramiko
    HAS_IMPORTED = True
except ImportError:
    HAS_IMPORTED = False
import sys

from ..module_utils import dd_connect
from ..module_utils import cmd_builder
import ansible.module_utils.common.json
import ansible.module_utils.compat.importlib
import json
from ..module_utils.cmd_templates import net

DOCUMENTATION = r'''
---
module: net
short_description: This module is used to manage the network on datadomain
version_added: "1.0.0"
description: This module supported below actions on network
    net aggregate add $virtual_ifname interfaces $physical_ifname $aggregate
    net aggregate del $virtual_ifname interfaces $physical_ifname
    net aggregate modify $virtual_ifname $aggregate
    net config $ifname $ipaddr $netmask
    net create interface $ifname
    net create virtual veth$vethid
    net destroy $ifname
    net enable $ifname
    net failover add $virtual_ifname interfaces $ifname $failover
    net failover del $virtual_ifname interfaces $ifname
    net failover modify $virtual_ifname $failover
    net hosts add $host_list
    net hosts del $ipaddr
    net hosts reset
    net lookup $ipaddr
    net ping $ipaddr
    net reset domainname
    net reset searchdomains
    net reset dns
    net reset hostname
    net route add net $network netmask $netmask gw $gateway dev $ifname
    net route add host $ipaddr gw $gateway dev $ifname
    net route del net $network netmask $netmask gw $gateway dev $ifname
    net route del host $ipaddr gw $gateway dev $ifname
    net set domainname $domainname
    net set searchdomains $searchdomains
    net set dns $dns
    net set hostname $hostname

options:
    state:
        description: Use following options to select the action
        type: str
        choices: [config, create, disable, enable, add, del, reset, set, destroy, test, modify] 
        required: True
    ifname:
        description: interface name
        type: str
    ipaddr:
        description: IP address
        type: str
    netmask:
        description: Subnet mask 
        type: str
    gateway:
        description: Gateway for the network/Ip
        type: str
    mtu:
        description: Maximum Transmission unit
        type: int
    vethid:
        description: virtual ethernet number.
        type: str
    physical-ifname:
        description:  Physical interface names like eth4a
        type: str
    virtual-ifname:
        description: virtual interface name like veth4
        type: str
    vlan:
        description: VLAN ID
        type: int
    network:
        description: Network IP 
        type: str
    option:
        description: Choose on which network attribute you want to run command
        type: str
        choices: [hosts, route, dns, hostname, domainname, searchdomains, ping, lookup, aggregate, failover]
    host-list:
        description: Use when you want to add hosts entry on Data domain Host list in the format IP FQDN hostname 
        type: str,
    count:
        description: Use when you want to perform ping test on IP. Specify how many times you want to ping the IP
        type: str,
    domainname:
        description: Domain name for the data domain
        type: str,
    searchdomains:
        description: Search domain names
        type: str,
    hostname:
        description: Hostname for the data domain
        type: str,
    dns:
        description: DNS IPs 
        type: str,
    aggregate:
        description: Select aggregate attributes
        type: dict
        options:
            mode:
                description: Aggregate mode
                type: str
                choices: [roundrobin, balanced, lacp]
            hash:
                description: Hash mode
                type: str
                choices: [xor-L2, xor-L3L4, xor-L2L3]
    failover:
        description: select failover attribute
        type: dict
        options: 
            primary:
                description: Select primary physical interface
                type: str
        
author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
  - name:  Add slave interfaces to an aggregate interface
    dellemc.datadomain.net:
        state: add
        option: aggregate
        virtual-ifname: veth0
        physical-ifname: eth5a eth4a
        aggregate:
            mode: lacp
            hash: xor-L3L4

  - name:  Show Network settings
    dellemc.datadomain.net:
        state: show
        
  - name:  Delete network interfaces from an aggregate interface
    dellemc.datadomain.net:
        state: del
        option: aggregate
        virtual-ifname: veth0
        physical-ifname: eth5a
   
  - name:  Modify the configuration of an aggregate interface
    dellemc.datadomain.net:
        state: modify
        option: aggregate
        virtual-ifname: veth0
        aggregate:
            hash: xor-L2L3

  - name:  Configure an Ethernet interface.
    dellemc.datadomain.net:
        state: config
        ifname: veth0.2345
        ipaddr: 100.64.65.149
        netmask: 255.255.255.240
        mtu: 9600 # Optional Parameter

  
  - name: Create a VLAN interface
    dellemc.datadomain.net:
        state: create
        ifname: veth0
        vlan: 2639

  - name: Create a virtual interface
    dellemc.datadomain.net:
        state: create
        vethid: '01'
 
  - name: Destroy a VLAN interface
    dellemc.datadomain.net:
        state: destroy
        ifname: veth01.2639
                                       
  - name: Enable an Ethernet interface
    dellemc.datadomain.net:
        state: enable
        ifname: veth01.2639

  - name:  Add network interfaces to a failover interface
    dellemc.datadomain.net:
        state: add
        option: failover
        virtual-ifname: veth0
        ifname: eth1a eth2b
        failover:
            primary: eth1a

                                    
  - name: Delete network interfaces from a failover interface
    dellemc.datadomain.net:
        state: del
        option: failover
        virtual-ifname: veth0
        ifname: eth1a
                   
  - name: Modify the primary network interface for a failover interface
    dellemc.datadomain.net:
        state: modify
        option: failover
        virtual-ifname: veth0
        failover:
            primary: eth2a                                      
   - name: Add a host list entry
    dellemc.datadomain.net:
        state: add
        option: hosts
        host-list: 100.64.65.100    a001us034nve001.usp01.xstream360.cloud  a001us034nve001

  - name: Delete a host list entry
    dellemc.datadomain.net:
        state: del
        option: hosts
        ipaddr: 100.64.65.100

  - name: Clear the hosts list
    dellemc.datadomain.net:
        state: reset
        option: hosts

  - name: Lookup DNS entries
    dellemc.datadomain.net:
        state: test
        option: lookup
        ipaddr: 100.64.65.150

  - name: Ping a host
    dellemc.datadomain.net:
        state: test
        option: ping
        ipaddr: 100.64.65.150
        count: 3

  - name: Reset (to default) the domainname
    dellemc.datadomain.net:
        state: reset
        option: domainname

  - name:  Reset (to default) the searchdomains
    dellemc.datadomain.net:
        state: reset
        option: searchdomains
  
  - name: Reset (to default) the DNS list
    dellemc.datadomain.net:
        state: reset
        option: dns 
        
  - name: Reset (to default) the hostname
    dellemc.datadomain.net:
        state: reset
        option: hostname

  - name: Add a network route rule
    dellemc.datadomain.net:
        state: add
        option: route
        network: 100.64.65.144
        gateway: 100.68.65.97
        netmask: 255.255.255.240
        ifname: eth0.2639	

  - name:  Add a host route rule
    dellemc.datadomain.net:
        state: add
        option: route
        ipaddr: 100.64.65.150
        gateway: 100.68.65.97
        ifname: eth0.2639
  

  - name: Remove a host routing rule
    dellemc.datadomain.net:
        state: del
        option: route
        ipaddr: 100.64.65.150
        gateway: 100.68.65.97
        ifname: eth0.2639

  - name: Remove a network routing rule
    dellemc.datadomain.net:
        state: del
        option: route
        network: 100.64.65.144
        netmask: 255.255.255.240
        gateway: 100.68.65.97
        ifname: eth0.2639

  - name: Set the domainname
    dellemc.datadomain.net:
        state: set
        option: domainname
        domainname: abc.com

  - name: Set the searchdomains
    dellemc.datadomain.net:
        state: set
        option: searchdomains
        searchdomains: abc.com
                               
  - name: Set the dns
    dellemc.datadomain.net:
        state: set
        option: dns
        dns: 10.15.10.2 10.15.2.10
  
   - name: Set the hostname
     dellemc.datadomain.net:
        state: set
        option: hostname
        hostname: a001us033dd1003
'''


def main():
    conditions, supported_commands = net()
    fields = {
        'state': {'type': 'str', 'choices':['config', 'create', 'disable', 'enable', 'add', 'del',
                                            'reset', 'set', 'destroy', 'test', 'modify', 'show'], 'required': True},
        'ifname': {'type': 'str'},
        'ipaddr': {'type': 'str'},
        'netmask': {'type': 'str'},
        'gateway': {'type': 'str'},
        'mtu': {'type': 'int'},
        'vethid': {'type': 'str'},
        'physical-ifname': {'type': 'str'},
        'virtual-ifname': {'type': 'str'},
        'vlan': {'type': 'int'},
        'network': {'type': 'str'},
        'option': {'type': 'str', 'choices': ['hosts', 'route', 'dns', 'hostname', 'domainname',
                                              'searchdomains', 'ping', 'lookup', 'aggregate', 'failover']},
        'host-list': {'type': 'str'},
        'count': {'type': 'str'},
        'domainname': {'type': 'str'},
        'searchdomains': {'type': 'str'},
        'hostname': {'type': 'str'},
        'dns': {'type': 'str'},
        'aggregate': {'type': 'dict', 'options':{'mode': {'type': 'str', 'choices': ['roundrobin', 'balanced', 'lacp']},
                                                'hash': {'type': 'str', 'choices': ['xor-L2', 'xor-L3L4', 'xor-L2L3']}}},
        'failover': {'type': 'dict', 'options':{'primary': {'type': 'str'}}},
        'host': {'type': 'str', 'required': True},
        'port': {'type': 'int', 'default': 22},
        'username': {'type': 'str', 'required': True},
        'private_key': {'type': 'str', 'no_log': True},
        'password': {'type': 'str', 'no_log': True},
    }

    module = AnsibleModule(argument_spec=fields, mutually_exclusive=[('private_key', 'password')],
                           required_one_of=[('private_key', 'password')])

    meta_output = []
    arg_dict = {}
    for key, value in module.params.items():
        if value is not None:
            dict_value = {}
            if isinstance(value, dict):
                for k, v in value.items():
                    if v is not None:
                        dict_value[k] = v
                arg_dict[key] = dict_value
            else:
                arg_dict[key] = value

    server = module.params['host']
    user = module.params['username']
    port = module.params['port']
    private_key = module.params['private_key']
    password = module.params['password']
    keys_to_delete = ['host', 'username', 'private_key', 'password']
    for key in keys_to_delete:
        if key in arg_dict:
            del arg_dict[key]

    cmd_output = {}
    changed = False
    action = cmd_builder.condition_check(conditions=conditions, command_build_dict=arg_dict)
    if len(action) > 0:
        command, will_change, is_filter, header = cmd_builder.build_command(action=action, arg_dict=arg_dict, supported_commands=supported_commands, conditions=conditions)
        cmd_output = cmd_builder.run_cmd(module=module, command=command, is_filter=is_filter, server=server,
                                         user=user, port=port, private_key=private_key, password=password, header=header)
        changed = will_change
        if 'show' in str(command):
            jsonout = dd_connect.tab_to_json(cmd_output['output'], header)
            cmd_output['output'] = jsonout
    else:
        state = arg_dict['state']
        possible_options = {}
        for key, value in conditions.items():
            if conditions[key]['state'] == state:
                possible_options = conditions[key]
        cmd_output['output'] = possible_options
        cmd_output['failed'] = True
    module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=changed)


if __name__ == '__main__':
    main()
