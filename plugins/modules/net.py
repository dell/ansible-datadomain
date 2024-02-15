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
from ..module_utils.action import adminaccess
from string import Template
import copy
import re

DOCUMENTATION = r'''
---
module: net
short_description: This module enables you to manage network properties of data domain.
version_added: "1.0.0"
description: The net command manages the use of all IP network features and displays network information and status.
  
options:
config:
  required: false
  type: dict
  description: Specify Interface configuration for creating new interface or modifying interface properties
  option:
    alias:
      required: false
      type: str
      description: IP Alias Interface
    autoneg:
      required: false
      type: bool
      description: Specify this option to configure the interface to autonegotiate the duplex and speed settings with the remote interface.
    destroy:
      required: false
      type: bool
      description: Use yes/true to destroy interface. If this option is absent, interface will be disabled.
    dhcp:
      required: false
      type: bool
      description: Set the dhcp option to yes to configure the interface to receive the IP address configuration from a DHCP server, and set this option to no when you want to manually configure the IP address. The default option requests an IPv4 address from DHCP, but you can select either IPv4 or IPv6 when you enable DHCP. When you use DHCP, the IP address delivered by DHCP replaces any static IP address previously configured for the base interface.
    duplex:
      choices:
      - full
      - half
      required: false
      type: str
      description: Specify this option when you want to manually configure the duplex setting or speed. The speed settings are 10, 100, 1,000, or 10,000 Mbps. This option automatically disables autonegotiation on the interface. If speed is set but duplex is not, the option defaults to full duplex. Half duplex can only be used for 10 Mbps and 100 Mbps.
    ifname:
      required: false
      type: str
      description: Specify the interface to configure and one or more arguments to change the configuration.
    ipaddr:
      required: false
      type: str
      description: Specify an IPv4 address for the interface. The dhcp option should not be set or should be set to "no." The manual IP address configureation will turn off dhcp for the interface being configured.
    mtu:
      required: false
      type: int
      description: The range for the MTU size is 350 - 9000 for IPv4 and 1280 - 9000 for IPv6. To ensure backward compatibility DD OS accepts an MTU size of 9014, but sets it to 9000 if the MTU requested is greater than 9000 and less than or equal to 9014.
    netmask:
      required: false
      type: str
      description: Subnet mask for network IP address
    speed:
      choices:
      - '10'
      - '100'
      - '1000'
      - '10000'
      required: false
      type: int
      description: Specify speed the port is capable of using.
    txqueuelen:
      required: false
      type: int
      description: Specify the transmit queue length. The range is 500 to 10,000 packet pointers, and the default value is 1000.
    up:
      required: false
      type: bool
      description: Use the true/yes argument to bring up an interface with or without an IP address. (Using net enable fails if no IP address is configured on the interface.) Use the no/false argument to bring down an interface.
    vlan:
      required: false
      type: str
      description: Type VLAN number.

dns:
  required: false
  type: list
  description: Set the DNS server list using addresses for IP version 4, IP version 6, or both
domainname:
  required: false
  type: str
  description: Set the domain name used by the protection system.
hostname:
  required: false
  type: str
  description: 'Type the hostname for the system'
hosts:
  option:
    hostnames:
      required: false
      type: list
      description: 'Type the hostnames in list format to add in hosts file'
    ipaddr:
      required: false
      type: str
      description: 'Type IP address to add in hosts file'
  required: false
  type: dict
  description: 'Add Hosts entry on Data domain'
option:
  required: false
  type: dict
  description: 'Set or Reset network options'
route:
  option:
    dev:
      required: false
      type: str
      description: 'Device Name to route traffic'
    gateway:
      required: false
      type: str
      description: 'Getway IP to route traffic'
    ipversion:
      choices:
      - ipv4
      - ipv6
      required: false
      type: str
      description: 'IP Version IPv4 or IPv6. '
    net:
      required: false
      type: str
      description: 'Network IP address'
    netmask:
      required: false
      type: str
      description: 'Subnet mask for Network IP'
    src:
      required: false
      type: str
      description: ''
    table:
      required: false
      type: str
      description: 'Route Table ID'
    type:
      choices:
      - fixed
      - floating
      required: false
      type: str
      description: HA systems use two types of IP addresses. Use the fixed IP option for node-specific configuration/management, which can be static or DHCP, IPv6 SLAAC, or IPv6 Link Local.
  required: false
  type: dict
  description: Adding or deleting the route on data domain
searchdomains:
  required: false
  type: list
  description: Set the search domains name used by the protection system
state:
  choices:
  - present
  - absent
  required: true
  type: str
  description: Choose the option from the choices above

author:
    - Sudarshan Kshirsagar (@kshirs1)
'''


EXAMPLES = r'''
    - name: Create a VLAN interface
      dellemc.datadomain.net:
        state: present
        config:
            ifname: ethV1
            vlan: 2024
				
    - name: Add IP address on interface.
      dellemc.datadomain.net:
        state: present
        config:
        ifname: ethV1
        ipaddr: 10.0.0.1
        netmask: 255.255.255.0
          
    - name: Configure an Ethernet Interface.
        dellemc.datadomain.net:
        state: present
        config:
            ifname: ethV1
            mtu: 1500
		
    - name: Disable Ethernet Interface.
        dellemc.datadomain.net:
        state: absent
        config:
            ifname: ethV1
					
    - name: Destroy Ethernet Interface.
        dellemc.datadomain.net:
        state: absent
        config:
            ifname: ethV1
            destroy: yes
					
    - name: Add a host list entry
        dellemc.datadomain.net:
        state: present
        hosts:
            ipaddr: 10.64.2.1
            hostnames:
                - lohost
                - lohost.domain.com

    - name: Delete a host list entry
        dellemc.datadomain.net:
        state: absent
        hosts:
            ipaddr: 10.0.0.3

    - name: Reset a host list to default (Deleting all hosts entries)
        dellemc.datadomain.net:
        state: absent
        hosts: {}
					

    - name: Set a network option (One option at a time.)
        dellemc.datadomain.net:
        state: present
        option:
            net.ipv4.tcp_keepalive_intvl: 60

    - name: Reset a network option (One option at a time.)
        dellemc.datadomain.net:
        state: absent
        option:
            net.ipv4.tcp_keepalive_intvl: ''
					
    - name: Add a routing rule
        dellemc.datadomain.net:
        state: present
        route:
            net: 100.64.35.0
            netmask: 255.255.255.0
            getway: 10.60.41.1 
            dev: ethV0

    - name: Delete a routing rule
        dellemc.datadomain.net:
        state: absent
        route:
            net: 100.64.35.0
					

    - name: Set a Domainname
        dellemc.datadomain.net:
        state: present
        domainname: domain.com

    - name: Reset a Domainname
        dellemc.datadomain.net:
        state: absent
        domainname: ''

    - name: Set a Searchdomains
        dellemc.datadomain.net:
        state: present
        searchdomains: 
            - domain.com
            - domain2.com

    - name: Reset a Searchdomains
        dellemc.datadomain.net:
        state: absent
        searchdomains: []

    - name: Set a dns
        dellemc.datadomain.net:
        state: present
        dns: 
            - 8.8.8.8
            - 8.8.8.9

    - name: Reset a dns
        dellemc.datadomain.net:
        state: absent
        dns: []
				
    - name: Set a hostname
        dellemc.datadomain.net:
        state: present
        hostname: datadomain.domain.com

    - name: Reset a hostname
        dellemc.datadomain.net:
        state: absent
        hostname: ''			

'''


def tab_to_json(output, header=None, rename_keys=None):
    final_data = []
    if rename_keys is None:
        rename_keys = {}
    if 'DNS servers configured manually' in str(output) or 'Searchdomains' in str(output):
        commandOut = output.split('\n')
        lookup = "--"
        i = 0
        p = 0
        out = {}
        data_frames = []
        for line in commandOut:
            i += 1
            if lookup in line:
                out[p] = i - 1
                p += 1
        p = 0
        total_lines = len(out) - 1
        if total_lines == 0:
            out[1] = out[0] + 2
            total_lines = 1
        while p < total_lines:
            start_line = out[p] + 1
            p += 1
            end_line = out[p]
            data_frames.append(commandOut[start_line:end_line])
        data = {}
        for line in data_frames:
            for l in line:
                obj = re.split('\s\s\s+', l.strip())
                if 'local domain' in obj[1]:
                    obj[1] = obj[1].split(' ')[0]
                i = 0
                
                if header[0] not in data:
                    data[header[0]] = []
                
                data[header[0]].append(obj[1])
                
        return data
    elif 'The Route Config list is:' in str(output):
        commandOut = output.strip().split('\n')
        
        for line in commandOut:
            data = {}
            if 'The Route Config list is:' not in str(line):
                line = line.strip().split(' ')
                v = 1
                k = 0
                while v <= len(line):
                    data[line[k]] = line[v]
                    k = k + 2
                    v = v + 2
                final_data.append(data)        
        return final_data
    elif 'Currently Set Options' in str(output):
        commandOut = output.strip().split('\n')
        data = {}
        for line in commandOut:
            if 'Currently Set Options' not in line:
                option, value = line.strip().replace(' is set to ', ',').split(',')
                option = option.replace('"', '').strip()
                data[option] = value.replace('"', '').replace('.', '').strip() 
        return data
    elif 'Hostname Mappings' in str(output):
        commandOut = output.strip().split('\n')
        data = {}
        for line in commandOut:
            
            if 'Hostname Mappings' not in line:
                ipaddr, hosts = line.strip().replace(' -> ', ',').split(',')
                data['ipaddr'] = ipaddr
                data['hostnames'] = hosts.split(' ')
        
        return data
    elif "--" in str(output) and "Option" not in str(output) and '- share' not in str(output):
        commandOut = output.split('\n')
        lookup = "--"
        i = 0
        p = 0
        out = {}
        data_frames = []
        for line in commandOut:
            i += 1
            if lookup in line:
                out[p] = i - 1
                p += 1
        p = 0
        total_lines = len(out) - 1
        if total_lines == 0:
            out[1] = out[0] + 2
            total_lines = 1
        while p < total_lines:
            start_line = out[p] + 1
            p += 1
            end_line = out[p]
            data_frames.append(commandOut[start_line:end_line])
        for line in data_frames:
            for l in line:
                data = {}
                obj = re.split('\s\s\s+', l.strip())
                i = 0
                if len(obj) >= (len(header) - 1):
                    for o in obj:
                        if 'n/a' in o:
                            o = ''
                        if 'local domain' in o:
                            o = o.split(' ')[0]
                        data[header[i]] = o
                        i = i + 1
                    final_data.append(data)
        return final_data
    elif "Option" in str(output) and 'Value' in str(output):
        cmdOutput = output.split('\n\n')
        for section in cmdOutput:
            data = {}
            section = section.strip()
            lines = section.split('\n')

            if ':' in lines[0]:
                mkey = lines[0].strip().replace(':', '')
                data[mkey] = {}
                for line in lines[1:]:
                    if '--' not in line and 'Option' not in line:
                        key, value = re.split('\s\s+', line.strip())
                        if key in rename_keys:
                            key = rename_keys[key]
                        data[mkey][key] = value
                final_data.append(data)
            else:
                mkeys = re.split('\s\s+', lines[0].strip())
                data = {}
                if 'Option' in mkeys:
                    for line in lines[1:]:
                        if '--' not in line and len(line) > 0:
                            key, value = re.split('\s\s+', line.strip())
                            if 'default' in value:
                                value = value.split(' ')[0]
                            
                            if key in rename_keys:
                                key = rename_keys[key]
                            data[key] = value
                    final_data.append(data)
                else:
                    for line in lines[1:]:
                        data = {}
                        if '--' not in line and 'Option' not in line:
                            values = re.split('\s\s+', line.strip())
                            i = 0
                            for value in values:
                                if 'default' in value:
                                    value = value.split(' ')[0]
                                key = mkeys[i]
                                if key in rename_keys:
                                    key = rename_keys[key]
                                data[key] = value
                                i += 1
                            final_data.append(data)
        return final_data
    elif ': ' in str(output):
        cmdOutput = output.split('\n\n')
        for line in cmdOutput:
            if len(line.strip()) > 0:
                obj = line.split('\n')
                data = {}
                for o in obj:
                    if ":" in o:
                        key, value = o.strip().split(":", 1)
                        if key in rename_keys:
                            key = rename_keys[key]
                        else:
                            key = key.strip().lower().replace(' ', '_')
                        if len(value.strip()) > 0:

                            data[key] = value.strip()
                        else:
                            data[key] = []
                    else:
                        if len(o) > 0 and '*' not in o:
                            try:
                                key, value = re.split('\s\s+', o.strip())
                                
                                if key in rename_keys:
                                    key = rename_keys[key]
                                else:
                                    key = key.lower().replace(' ', '_')
                                data[key] = value.strip()
                            except Exception as e:
                                # print(e)
                                pass

                final_data.append(data)
        return final_data
    else:
        data = {}
        data['output'] = []
        cmdOutput = output.split('\n')
        for line in cmdOutput:
            if len(line) > 0:
                data['output'].append(line)
        final_data.append(data)
        return final_data


def condition_check(conditions, command_build_dict):
    diff_keys = []
    action = ''
    query_out = []
    for key, value in conditions.items():
        query_out = []
        diff_keys = []
        for obj in conditions[key]['req_key']:
            if obj not in command_build_dict:
                diff_keys.append(obj)
        if len(diff_keys) == 0:
            for query_key, query_value in conditions[key]['query'].items():
                try:
                    if command_build_dict[query_key] == query_value:
                        query_out.append(True)
                    else:
                        query_out.append(False)
                except KeyError:
                    query_out.append(False)
                    pass
            if all(query_out):
                action = key
                try:
                    check_status_ep = value['check_status_ep']
                except KeyError:
                    check_status_ep=None   
                break
    return action


def net():
    conditions = dict(
        net_route=dict(query=dict(), req_key=['route'], opt_key=[], will_change=True, header=None),
        net_option=dict(query=dict(), req_key=['option'], opt_key=[], will_change=True, header=None),
        net_hosts=dict(query=dict(), req_key=['hosts'], opt_key=[], will_change=True, header=None),
        net_domainname=dict(query=dict(), req_key=['domainname'], opt_key=[], will_change=True, header=None),
        net_searchdomains=dict(query=dict(), req_key=['searchdomains'], opt_key=[], will_change=True, header=None),
        net_dns=dict(query=dict(), req_key=['dns'], opt_key=[], will_change=True, header=None),
        net_hostname=dict(query=dict(), req_key=['hostname'], opt_key=[], will_change=True, header=None),
        net_service=dict(query=dict(), req_key=['config'], opt_key=[], will_change=True, header=None))
    
    command_template = dict(net_route={'show': '["net route show config"]',
                                         'add':'["net route add"]',
                                         'del':'["net route del"]',
                                         },

                            net_option={'show': '["net option show"]',
                                         'set':'["net option set"]',
                                         'reset':'["net option reset"]',
                                         },
                            net_hosts={'show': '["net hosts show"]',
                                         'add':'["net hosts add"]',
                                         'del':'["net hosts del"]',
                                         'reset': '["net hosts reset"]',
                                         },
                            net_domainname={'show': '["net show domainname"]',
                                         'set':'["net set domainname $domainname"]',
                                         'reset':'["net reset domainname"]',
                                         },
                            net_searchdomains={'show': '["net show searchdomains"]',
                                         'set':'["net set searchdomains $searchdomains"]',
                                         'reset':'["net reset searchdomains"]',
                                         },
                            net_hostname={'show': '["net show hostname"]',
                                         'set':'["net set hostname $hostname"]',
                                         'reset':'["net reset hostname"]',
                                         },
                            net_dns={'show': '["net show dns"]',
                                         'set':'["net set dns $dns"]',
                                         'reset':'["net reset dns"]',
                                         },
                            net_service={'show': '["net show settings"]',
                                         'add':'["net create interface $ifname"]',
                                         'destroy':'["net destroy $ifname"]',
                                         'mod':'["net config $ifname"]',
                                         'enable': '["net enable $ifname"]',
                                         'disable': '["net disable $ifname"]',
                                         },
                                         )
    
    headers = dict(net_service=['ifname', 'up', 'state', 'dhcp', 'ipaddr', 'netmask', 'type', 'additional setting'],
                    net_dns=['dns'],
                    net_hostname=[],
                    net_searchdomains=['searchdomains'],
                    net_domainname=[''],
                    net_hosts=[],
                    net_option=[],
                    net_route=[],
                    )
    rename_keys = dict(net_service={},
                    net_dns={},
                    net_hostname={'The Hostname is': 'hostname'},
                    net_searchdomains={},
                    net_domainname={'The Domainname is': 'domainname'},
                    net_hosts={},
                    net_option={},
                    net_route={},
                    )
    return conditions, command_template, headers, rename_keys


def build_commands(modify, action, arg_dict, obj_key, cmd_templates, config_to_modify=None):
    commands = {}
    payload = {}
    # if obj_key is None:
    #     obj_key = []

    if obj_key is None:
        narg_dict = copy.deepcopy(arg_dict)
    else:
        narg_dict = copy.deepcopy(arg_dict[obj_key])
    keys_to_remove = ['state', 'port']
    
    keys_in_dict = list(narg_dict.keys())
    
    for key in keys_in_dict:
        if key in keys_to_remove:
            del narg_dict[key]
    keys_required_for_payload = {}
    for mod in modify:
        command_to_run = ''
        cmd = cmd_templates[action][mod]
        # if mod == 'show':
        command_to_run = ''
        
        command_template = Template(cmd)
        command = eval(command_template.substitute(**narg_dict))
        
        mod_to_check = ['show', 'enable', 'disable', 'destroy']
        if mod not in mod_to_check:
            if obj_key is not None:
                if mod == 'reset':
                    if len(narg_dict) > 0:
                        for key in narg_dict:
                            command.append(key)
                            break
                    else:
                        command = command
                elif mod == 'add':
                    if obj_key == 'hosts':
                        for key, value in narg_dict.items():
                            command.append(value)
                    elif obj_key == 'config':
                        if 'vlan' in narg_dict or 'alias' in narg_dict:
                            for key, value in narg_dict.items():
                                
                                if key == 'vlan':
                                    command.append(key)
                                    command.append(value)
                                    break
                                if key == 'alias':
                                    command.append(key)
                                    command.append(value)
                                    break
                        else:
                            command = []
                    else:
                        for key, value in config_to_modify[mod].items():
                            if key == 'getway':
                                key = 'gw'
                            command.append(key)
                            command.append(value)
            
                elif mod == 'mod':            
                    if 'autoneg' in narg_dict:
                        if narg_dict['autoneg']:
                            if 'duplex' in narg_dict:
                                del narg_dict['duplex']
                            if 'speed' in narg_dict:
                                del narg_dict['speed']

                    if 'dhcp' in narg_dict:
                        if not narg_dict['dhcp']:
                            if 'ipversion' in narg_dict:
                                del narg_dict['ipversion']
                        else:
                            if 'ipaddr' in narg_dict:
                                del narg_dict['ipaddr']
                            if 'netmask' in narg_dict:
                                del narg_dict['netmask']
                            if 'ipv6addr' in narg_dict:
                                del narg_dict['ipv6addr']
                    if 'ipaddr' in narg_dict:
                        if 'ipv6addr' in narg_dict:
                            del narg_dict['ipv6addr']
                    if 'ipv6addr' in narg_dict:
                        if 'ipaddr' in narg_dict:
                            del narg_dict['ipaddr']
                        if 'netmask' in narg_dict:
                            del narg_dict['netmask']       
                    if 'vlan' in narg_dict:
                        del narg_dict['vlan']
                    if 'alias' in narg_dict:
                        del narg_dict['alias']
                    
                    for key, value in narg_dict.items():
                        if key == 'autoneg':
                            if value:
                                command.append(key)
                        elif key == 'ipaddr' or key == 'ipv6addr':
                            command.append(value)
                        elif key == 'up':
                            if value:
                                command.append(key)
                            else:
                                command.append('down')

                        else:
                            if key != 'ifname':
                                command.append(key)
                                command.append(value)
                
                elif mod == 'del':
                    if obj_key == 'hosts':
                        for key, value in narg_dict.items():
                            if key == 'ipaddr':
                                command.append(value)
                    elif obj_key == 'route':
                        for key, value in config_to_modify[mod].items():
                            command.append(value)
                    else:
                        
                        for key, value in config_to_modify[mod].items():
                            command.append(key)
                            command.append(value)
  
                else:
                    for key, value in config_to_modify[mod].items():
                        command.append(key)
                        command.append(value)
 
            else:
                pass
        for arg in command:
            command_to_run = command_to_run + " " + str(arg)
        if command_to_run not in commands:
            command_to_run = command_to_run.replace('[', '').replace("'", '').replace(']', '').strip()
            commands[mod] = command_to_run

    return commands, payload      


def get_obj_key(arg_dict, obj_keys):
    for obj in obj_keys:
        if obj in arg_dict:
            return obj
            break


def check_if_object_present_absent(server, user, password, obj_key=None, command=None, endpoint=None, failed_cmd_out=None, headers=None, search_obj=None, rename_keys=None):
    port = 22
    if command is not None:
        cmd_output = dd_connect.dd_ssh(server, user, port, command, private_key=None, password=password, header=headers)
        jsonout = tab_to_json(cmd_output['output'], header=headers, rename_keys=rename_keys)
        
        config = []
        if obj_key == 'config':
            status_code = False
            for netconfig in jsonout:
                # if 'vlan' in netconfig:
                #     ifname = netconfig['ifname'].netconfig['vlan']
                # elif 'alias' in netconfig:
                #     ifname = netconfig['ifname'].netconfig['alias']
                # else:
                #     ifname = netconfig['ifname']
                if netconfig['ifname'] == search_obj:
                    status_code = True
                    config.append(netconfig)
                    break
            if len(config) == 0:
                jsonout = config        
        else:
            status_code = True
        if len(config) > 0:
            jsonout = config
        if not cmd_output['failed']:
            for fcode in failed_cmd_out:
                if fcode in str(cmd_output['output']):
                    status_code = False
                    break
            if status_code:
                return [True, jsonout]
            else:
                return [False, jsonout]
        else:
            return [False, jsonout]     


def check_if_modify_required(arg_dict, obj_key, obj_config):
    modify = []
    config_to_modify = {}
    keys_to_remove = ['state', 'port']
    temp_req_config = {}

    if obj_key is not None:
        temp_req_config = copy.deepcopy(arg_dict[obj_key])
    else:
        temp_req_config = copy.deepcopy(arg_dict)
    for key in arg_dict:
        if key in keys_to_remove:
            if key in temp_req_config:
                del temp_req_config[key]
    
    if arg_dict['state'] == 'present':
        if obj_key is not None:
            if obj_key == 'config':
                net_config = obj_config[0]
                for key, value in temp_req_config.items():
                    if key != 'ifname':
                        if key in net_config:
                            if value == net_config[key]:
                                pass
                            else:
                                if 'mod' not in modify:
                                    modify.append('mod')
                                if 'mod' not in config_to_modify:
                                    config_to_modify['mod'] = {}
                                config_to_modify['mod'][key] = value
                        else:
                            if 'mod' not in modify:
                                    modify.append('mod')
                            if 'mod' not in config_to_modify:
                                config_to_modify['mod'] = {}
                            config_to_modify['mod'][key] = value   

            elif obj_key == 'hosts':
                if 'No hostname mappings' in str(obj_config):
                    obj_config = {}
                    obj_config['ipaddr'] = ''
                if temp_req_config['ipaddr'] == obj_config['ipaddr']:
                    hostname_to_update = []
                    for value in temp_req_config['hostnames']:
                        if value in obj_config['hostnames']:
                            pass
                        else:
                            if 'add' not in modify:
                                modify.append('add')
                            if 'add' not in config_to_modify:
                                config_to_modify['add'] = {}
                                config_to_modify['add']['hostnames'] = []
                            config_to_modify['add']['hostnames'].append(value)
                else:
                    if 'add' not in modify:
                        modify.append('add')
                    if 'add' not in config_to_modify:
                        config_to_modify['add'] = {}
                        config_to_modify['add']['hostnames'] = []
                    config_to_modify['add']['hostnames'].append(temp_req_config['hostnames'])  
            
            elif obj_key =='option':
                for key in temp_req_config:
                    if key not in obj_config:
                        if 'set' not in modify:
                            modify.append('set')
                        if 'set' not in config_to_modify:
                            config_to_modify['set'] = {}
                        config_to_modify['set'][key] = temp_req_config[key]
                        break
                    else:
                        if str(temp_req_config[key]) == str(obj_config[key]):
                            pass
                        else:
                            if 'set' not in modify:
                                modify.append('set')
                            if 'set' not in config_to_modify:
                                config_to_modify['set'] = {}
                            config_to_modify['set'][key] = temp_req_config[key]
                            break
        
            elif obj_key =='route':
                for route in obj_config:
                    if 'The Route Config list is empty' in str(route):
                        route['net'] = ''
                    if route['net'] == temp_req_config['net']:
                        pass
                    else:
                        if 'add' not in modify:
                            modify.append('add')
                        if 'add' not in config_to_modify:
                            config_to_modify['add'] = {}
                        config_to_modify['add'] = temp_req_config               

        else:
            for key in temp_req_config:
                if isinstance(obj_config, list):
                    for config in obj_config:
                        if 'output' in config:
                            obj_config = {}
                            obj_config[key] = ''
                else:
                    if 'output' in obj_config:
                        obj_config = {}
                        obj_config['key'] = ''
                if isinstance(obj_config, list):
                    if len(obj_config) == 1:
                        obj = obj_config[0][key]
                else:
                    obj = obj_config[key]
                    if isinstance(obj, list):
                        obj.sort()
                        temp_req_config[key].sort()
                if temp_req_config[key] == obj:
                    pass
                else:
                    if isinstance(obj, list):
                        for item in temp_req_config[key]:
                            if item not in obj:
                                if 'set' not in modify:
                                    modify.append('set')
                                if 'set' not in config_to_modify:
                                    config_to_modify['set'] = {}
                                if key not in config_to_modify['set']:
                                    config_to_modify['set'][key] = []
                                config_to_modify['set'][key].append(item)
                    else:  
                        if 'set' not in modify:
                            modify.append('set')
                        if 'set' not in config_to_modify:
                            config_to_modify['set'] = {}
                        config_to_modify['set'][key] = temp_req_config[key] 
    
    else:
        if obj_key is not None:
            if obj_key == 'route':
                for route in obj_config:
                    if 'The Route Config list is empty' in str(route):
                        route['net'] = ''
                    if route['net'] == temp_req_config['net']:
                        if 'del' not in modify:
                            modify.append('del')
                        if 'del' not in config_to_modify:
                            config_to_modify['del'] = {}
                        config_to_modify['del']['net'] = route['net'] 
                
                    else:
                        pass
            elif obj_key == 'config':
                if obj_config[0]['ifname'] == temp_req_config['ifname']:
                    if 'destroy' in temp_req_config:
                        if temp_req_config['destroy']:
                            if 'destroy' not in modify:
                                    modify.append('destroy')
                            if 'destroy' not in config_to_modify:
                                config_to_modify['destroy'] = {}
                            config_to_modify['destroy']['ifname'] = temp_req_config['ifname']
                        else:
                            if 'disable' not in modify:
                                    modify.append('disable')
                            if 'disable' not in config_to_modify:
                                config_to_modify['disable'] = {}
                            config_to_modify['disable']['ifname'] = temp_req_config['ifname']
                    else:
                        if 'disable' not in modify:
                                modify.append('disable')
                        if 'disable' not in config_to_modify:
                            config_to_modify['disable'] = {}
                        config_to_modify['disable']['ifname'] = temp_req_config['ifname']

            elif obj_key == 'hosts':
                if len(temp_req_config) > 0:
                    if 'No hostname mappings' in str(obj_config):
                        obj_config = {}
                        obj_config['ipaddr'] = ''
                    if temp_req_config['ipaddr'] == obj_config['ipaddr']:
                        if 'del' not in modify:
                            modify.append('del')
                        if 'del' not in config_to_modify:
                            config_to_modify['del'] = {}
                        config_to_modify['del']['ipaddr'] = temp_req_config['ipaddr']
                else:
                    if 'reset' not in modify:
                        modify.append('reset')
                    if 'reset' not in config_to_modify:
                        config_to_modify['reset'] = {}
                    # config_to_modify['reset']['ipaddr'] = temp_req_config['ipaddr']
            elif obj_key == 'option':
                for key in temp_req_config:
                    if key in obj_config:
                        if 'reset' not in modify:
                            modify.append('reset')
                        if 'reset' not in config_to_modify:
                            config_to_modify['reset'] = {}
                        config_to_modify['reset']['key'] = key
                        break
        else:
            if 'reset' not in modify:
                modify.append('reset')
            if 'reset' not in config_to_modify:
                config_to_modify['reset'] = {}
            # config_to_modify['reset']['key'] = key
    

    return modify, config_to_modify      


def change_object(server, user, password, command=None, endpoint=None, request_type=None, payload=None):
    port = 22
    if command is not None:
        cmd_output = dd_connect.dd_ssh(server, user, port, command, private_key=None, password=password, header=None)
        # jsonout = nfs_output(output=cmd_output['output'])
        if not cmd_output['failed']:
            return [True, cmd_output['output']]
        else:
            return [False, cmd_output['output']]
    elif endpoint is not None:
      cmd_output = dd_connect.dd_requests(server, user, api_pass=password, endpoint=endpoint, request_type=request_type, payload=payload, query_params=None, field_params=None)
      if not cmd_output['failed']:
          return [True,  cmd_output['output']]
      else:
          return [False,  cmd_output['output']]


def main():
    fields = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'required': True},
        'config':  {'type': 'dict', 'required': False, 'option': {
            'ifname': {'type': 'str', 'required': False},
            'ipaddr': {'type': 'str', 'required': False},
            'netmask': {'type': 'str', 'required': False},
            'dhcp': {'type': 'bool', 'required': False},
            'autoneg': {'type': 'bool', 'required': False},
            'duplex': {'type': 'str', 'choices': ['full', 'half'], 'required': False},
            'speed': {'type': 'int', 'choices': ['10', '100', '1000', '10000'], 'required': False},
            'up': {'type': 'bool', 'required': False},
            'mtu': {'type': 'int', 'required': False},
            'txqueuelen': {'type': 'int', 'required': False},
            'vlan': {'type': 'str', 'required': False},
            'alias': {'type': 'str', 'required': False},
            'destroy': {'type': 'bool', 'required': False}
        }},
        'hosts': {'type': 'dict', 'required': False, 'option':{
            'ipaddr': {'type': 'str', 'required': False},
            'hostnames':{'type': 'list', 'required': False},
        }},
        'option': {'type': 'dict', 'required': False},
        'route': {'type': 'dict', 'required': False, 'option': {
            'ipversion': {'type': 'str', 'choices': ['ipv4', 'ipv6'], 'required': False},
            'type': {'type': 'str', 'choices': ['fixed', 'floating'], 'required': False},
            'gateway': {'type': 'str', 'required': False},
            'net': {'type': 'str', 'required': False},
            'netmask': {'type': 'str', 'required': False},
            'dev': {'type': 'str', 'required': False},
            'src': {'type': 'str', 'required': False},
            'table': {'type': 'str', 'required': False},
        }},
        'domainname': {'type': 'str', 'required': False},
        'searchdomains': {'type': 'list', 'required': False},
        'hostname': {'type': 'str', 'required': False},
        'dns': {'type': 'list', 'required': False},
        'host': {'type': 'str', 'required': True},
        'port': {'type': 'int', 'default': 22},
        'username': {'type': 'str', 'required': True},
        'password': {'type': 'str', 'no_log': True},
        }
    
    module = AnsibleModule(argument_spec=fields, mutually_exclusive=[('private_key', 'password'), ('hosts', 'option', 'config', 'route')],
                          required_one_of=[('private_key', 'password')])
  
    server = module.params['host']
    user = module.params['username']
    port = module.params['port']
    password = module.params['password']
    meta_output = []
    arg_dict = {}
    for key, value in module.params.items():
        if isinstance(value, dict):
            if key not in arg_dict:
                arg_dict[key] = {}
            for kv, v in value.items():
                if v is not None:
                    arg_dict[key][kv] = v
        else:
            if value is not None:
                arg_dict[key] = value
    keys_to_delete = ['host', 'username', 'private_key', 'password']
    
    for key in keys_to_delete:
        if key in arg_dict:
            del arg_dict[key]
    cmd_output = {}

    conditions, cmd_templates, headers, rename_keys = net()
    failed_cmd_out = ['Device not found']
    obj_keys = ['route', 'option', 'hosts', 'config']
    obj_key = get_obj_key(arg_dict, obj_keys)
    action = condition_check(conditions, command_build_dict=arg_dict)
    modify = ['show']

    if len(action) > 0:
        commands, payload = build_commands(modify, action, arg_dict, obj_key, cmd_templates)
        if len(commands) > 0:
            for command in commands:
                search_obj = None
                if obj_key == 'config':
                    if 'vlan' in arg_dict['config']:
                        search_obj = arg_dict['config']['ifname'] + '.' + str(arg_dict['config']['vlan'])
                    elif 'alias' in arg_dict['config']:
                        search_obj = arg_dict['config']['ifname'] + '.' + str(arg_dict['config']['alias'])
                    else:
                        search_obj = arg_dict['config']['ifname']
                obj_exist, obj_config = check_if_object_present_absent(server, user, password, obj_key=obj_key, command=commands[command], endpoint=None, failed_cmd_out=failed_cmd_out, headers=headers[action], search_obj=search_obj, rename_keys=rename_keys[action])
                if obj_exist:
                    modify, config_to_modify = check_if_modify_required(arg_dict, obj_key, obj_config)
                    if len(modify) > 0:
                        commands, payload = build_commands(modify, action, arg_dict, obj_key, cmd_templates, config_to_modify=config_to_modify)
                        if len(commands) > 0:
                            for key in commands:
                                command = commands[key]
                                status, output = change_object(server, user, password, command=command, endpoint=None, request_type=None, payload=None)
                                # status = True
                                # output = command
                                if status:
                                    changed = True
                                    failed = False
                                else:
                                    changed = False
                                    failed = True
                                cmd_output['output'] = output
                                cmd_output['changed'] = changed
                                cmd_output['failed'] = failed
                        else:
                            cmd_output['output'] = obj_config
                            cmd_output['changed'] = False
                            cmd_output['failed'] = False
                    else:
                        cmd_output['output'] = obj_config
                        cmd_output['changed'] = False
                        cmd_output['failed'] = False    
                else:
                    if arg_dict['state'] == 'present':
                        modify = ['add']
                        commands, payload = build_commands(modify, action, arg_dict, obj_key, cmd_templates)
                        if len(commands) > 0:
                            for key in commands:
                                command = commands[key]
                                status, output = change_object(server, user, password, command=command, endpoint=None, request_type=None, payload=None)
                                
                                if status:
                                    changed = True
                                    failed = False
                                else:
                                    changed = False
                                    failed = True
                                cmd_output['output'] = output
                                cmd_output['changed'] = changed
                                cmd_output['failed'] = failed
                        else:
                            cmd_output['output'] = obj_config
                            cmd_output['changed'] = False
                            cmd_output['failed'] = False
    else:
        cmd_output['output'] = arg_dict #'Please check the input parameters and rerun the playbook.'
        cmd_output['failed'] = False
        cmd_output['changed'] = False
    
    module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=cmd_output['changed'])


if __name__ == '__main__':
    main()