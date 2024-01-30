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
module: ntp
short_description: This module is used to manage the configuration using ntp command.
version_added: "1.0.0"
description: This module is used to manage the configuration using ntp command.
  
options:
  state:
    type: str
    choices:
    - present, absent
    required: true
    description: 'Choose the option from the choices above'
  restart:
    type: bool
    description: Use this parameter to restart the nfs services. 
  version:
    type: str
    description: NFS Version to start, stop or restart NFS services. Currently DD supporting version 3 and 4. So you may type 3, 4 or all. If you do not mention this parameter, it will take version 3
  export:
    type: dict
    description: Provide Export Information
    options:
      name:
        type: str
        description: name of the export
      path:
        type: str
        description: Mtree path. Make sure export does not exists for this path already. Only required during export creation.
      destroy:
        type: bool
        description: If used with state = absent, it will destroy export.
      new_export_name:
        type: str
        description: New name to rename a export 
      clients:
        type: list
        description: Authorized the client information.
        suboptions:
          clientid:
            type: str
            description: A client can be a fully qualified domain hostname, a class-C IP address, an IP address with netmask or length, an IPV6 address, an NIS netgroup name with the prefix @, or an asterisk wildcard for the domain name such as *.yourcompany.com.  
          options:
            type: str
            description: The options-list is comma separated and enclosed by quotes if more than one option is provided. If no option is specified, the default options are sec=sys, rw, root_squash, no_all_squash, secure, and version=3.
      referrals:
        type: list
        description: referral location to the export.
        suboptions:
          referral:
            type: str
            description: defines the name of the referral
          remote-servers:
            type: str
            description: defines the remote network address or addresses to be used in the referral. The following must be true for each export - 1. Each referral location must refer to only one NFS server, although the server can contain multiple network addresses. 2. Each NFS server should be associated with only one referral location. 
          remote-path:
            type: str
            description: allows you to specify a remote path name. If you do not specify a path, the current export path is used.
  option:
    type: dict
    description: ''
    required: false
    suboptions:
      default-export-version:
        type: str   
        description: 'The default version or versions for client exports. This takes effect for future client exports only. Any legal version string is allowed (3, 3:4, all).' 
      default-server-version:
        description: 'Set the NFS server to use. NFSv3 is default. to make NFSv4 as the default use 4 as a value to this parameter.Any legal version string is allowed (3, 3:4, all).'
        type: str 
      nfs4-grace-period:
        type: str   
        description: 'The grace period for NFSv4 recovery measured in seconds. The minimum is 5 seconds; the maximum is 120 seconds. The default is 30 seconds.' 
      nfs4-lease-interval:
        type: str   
        description: 'The client lease interval measured in seconds. The minimum is 120 seconds, the maximum is 3600 seconds. The default is 300 seconds.' 
      mountd-port:
        type: str   
        description: 'The IP port for mountd. Changing this port requires an NFS server restart. The default port is 2052.' 
      nfs4-port:
        type: str   
        description: 'The IP port for the NFSv4 server. Changing this port requires an NFS server restart. The default port is 2049.' 
      nfs3-port:
        type: str   
        description: 'The IP port for the NFSv3 server and related protocols. Changing this port requires an NFS server restart. The default port is 2049.' 
      nfs4-domain:
        type: str   
        description: 'The NFSv4 sever domain. Any valid domain name is permitted. The protection system DNS domain name is the default; "" is the default if the domain name is not set.' 
      nfs4-idmap-out-numeric:
        type: str   
        description: 'Set output mapping of NFSv4 owner/group ids (e.g. fred@emc.com) as numeric values or names in output attributes and ACL ACE entries. The default is map-first; use numeric ID mapping if normal mapping fails. Use numeric ID mapping if allowed. Numeric IDs are never sent; if mapping fails, the server sends the ID “nobody”.' 
      nfs4-idmap-active-directory:
        type: str   
        description: 'Determine whether NFSv4 should use CIFS active directory (AD) for name resolution and ID mapping. Disabled is the default setting. Active-Directory mapping may be used to increase interoperability in a mixed CIFS/NFS environment.' 
      nfs4-acls:
        type: str   
        description: 'Determine whether NFSv4 ACLs (access control lists) are enabled. Disabled is the default setting.' 
      default-root-squash:
        type: str   
        description: 'Enabled is the default setting.' 
      force-minimum-root-squash-default:
        type: str   
        description: 'Disabled is the default setting.' 
      report-mtree-quota:
        type: str   
        description: 'Disabled is the default setting.' 

author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
	- name: Remove referral entry from an existing export
		dellemc.datadomain.nfs:
			state: absent
			export:
				name: backup
				referrals:
					- referral: remote
	- name: Remove client entry from an existing export
		dellemc.datadomain.nfs:
			state: absent
			export:
				name: backup
				clients:
					- clientid: 10.0.0.5

	- name: Add a client or a referral to an export
		dellemc.datadomain.nfs:
			state: present
			export:
				name: backup
				clients:
					- clientid: 10.0.0.5
						options: sec=sys,rw,root_squash,no_all_squash,secure,version=3
				referrals:
					- referral: remote
						remote-servers: 10.0.5.5
						remote-path: /data/col1/backup

	- name: Create an export, optionally add clients and/or referral
		dellemc.datadomain.nfs:
			state: present
			export:
				name: backup
				path: /data/col1/backup
				clients:
					- clientid: 10.0.0.5
						options: (sec=sys,rw,root_squash,no_all_squash,secure,version=3
				referrals:
					- referral: remote
						remote-servers: 10.0.5.5
						remote-path: /data/col1/backup
						
	- name: Destroy an export
		dellemc.datadomain.nfs:
			state: absent
			export:
				name: backup
				destroy: yes

	- name: Modify clients or referrals for one or more exports (if exists)
		dellemc.datadomain.nfs:
			state: present
			export:
				name: backup
				path: /data/col1/backup
				clients:
					- clientid: 10.0.0.5
						options: (sec=sys,rw,root_squash,no_all_squash,secure,version=4
				referrals:
					- referral: remote
						remote-servers: 10.0.5.5
						remote-path: /data/col1/backup2
						
	- name: Rename an export
		dellemc.datadomain.nfs:
			state: present
			export:
				name: backup
				new_export_name: backup1


	- name: Set an NFS option to a specified value
		dellemc.datadomain.nfs:
			state: present
			option:
				nfs4-grace-period: 30
				nfs4-lease-interval: 300
				
	- name: Reset a single/multiple NFS option to default values
		dellemc.datadomain.nfs:
			state: absent
			option:
				nfs4-grace-period: ''
				nfs4-lease-interval: ''

	- name: Disable NFS clients from connecting
		dellemc.datadomain.nfs:
			state: absent
			version: 3

	- name: Enable NFS clients to connect
		dellemc.datadomain.nfs:
			state: present
			version: 3
			
	- name: Restart NFS servers
		dellemc.datadomain.nfs:
			state: present
			version: 3
			restart: yes
'''

def nfs_output(output, header=None):
    i = 0
    dash_count = 0
    table_start_row = 0
    table_end_row = 0
    headers = []
    final_data = {'export':{}}
    cmd_out = output.split('\n')
    for line in cmd_out:
        if ':' in line and 'Referrals' not in line and 'Total' not in line:
            key, value = line.split(':')
            key = key.lower().strip()
            value = value.strip()
            if key == 'nfs export':
                key = 'name'
            else:
                key = key
            final_data['export'][key] = value
        elif '--' in line:
            dash_count = dash_count + 1
            ind = i - 1
            if (dash_count % 2) != 0:
                obj_list = []
                headers = re.split('\s\s\s+', cmd_out[ind].strip())
                if 'clients' not in final_data['export']:
                    final_data['export']['clients'] = []
               
        elif '--' not in line and len(line.strip()) > 0:
            if 'Referrals' not in line  and 'Total' not in line and 'Options' not in line and 'Name' not in line  and 'No' not in line:
               
                obj = re.split('\s\s\s+', cmd_out[i].strip())
                
                if 'Client' in headers:
                    headers[0] = 'clientid'
                if 'Name' in headers:
                    headers[0] = 'referral'

                obj_dict = {}
                h = 0
                for o in obj:
                   
                    header = headers[h].lower().replace(' ', '-')
                    o = o.replace('(', '').replace(')', '')
                    obj_dict[header] = o
                    h = h + 1
                obj_list.append(obj_dict)

            if dash_count == 2:
                final_data['export']['clients'] = obj_list

                if 'Referrals' in final_data['export']:
                    obj_list = []
                    final_data['export']['referrals'] = {}
            if dash_count == 4:
                final_data['export']['referrals'] = obj_list
        i = i + 1
    return final_data


def check_if_object_present_absent(server, user, password, command=None, endpoint=None, failed_cmd_out=None, headers=None):
    port = 22
    if command is not None:
        
        cmd_output = dd_connect.dd_ssh(server, user, port, command, private_key=None, password=password, header=None)
        
        # jsonout = output=cmd_output['output']
        if 'export' in command:
            jsonout = nfs_output(output=cmd_output['output'], header=headers)
        else:
            headers = ['option', 'value']
            jsonout = dd_connect.tab_to_json(output=cmd_output['output'], header=headers)
 
        if not cmd_output['failed']:
            if not failed_cmd_out in str(cmd_output['output']):
                return [True, jsonout]
            else:
                return [False, jsonout]
        else:
            return [False, jsonout]
    elif endpoint is not None:
        cmd_output = dd_connect.dd_requests(server, user, api_pass=password, endpoint=endpoint, request_type='get', payload=None, query_params=None, field_params=None)
        if not cmd_output['failed']:
            return [True,  cmd_output['output']]
        else:
            return [False,  cmd_output['output']]


def check_if_modify_required(action, arg_dict, obj_key, obj_config, mod_keys=None, command=None, endpoint=None):
    modify = []
    config_to_modify = {}

    if obj_key is not None:
        obj_config_tobe = copy.deepcopy(arg_dict[obj_key])
    else:
        obj_config_tobe = copy.deepcopy(arg_dict)
    keys_to_remove = ['state', 'port', 'name', 'path']
    for key in keys_to_remove:
        if key in obj_config_tobe:
            try:
                del obj_config_tobe[key]
            except KeyError:
                pass

    if arg_dict['state'] == 'present':    
        for key, value in obj_config_tobe.items():
            if obj_key is not None:
                if key in mod_keys[obj_key]: 
                     
                    if isinstance(value, list): 
                        for items in value:
                            num_match_clients = 0
                            num_match_referrals = 0
                            
                            if isinstance(items, dict):
                                if key in obj_config['export']:
                                    if key == 'clients':
                                        for config in obj_config['export'][key]:
                                            
                                            if items['clientid'] == config['clientid']:
                                                num_match_clients = num_match_clients + 1
                                                if items['options'] == config['options']:
                                                    pass
                                                else:
                                                    if 'mod' not in modify:
                                                        modify.append('mod')
                                                        config_to_modify['modc'] = [items]
                                                    else:
                                                        if 'modc' not in config_to_modify:
                                                            config_to_modify['modc'] = [items]
                                                        else:
                                                            config_to_modify['modc'].append(items)

                                          
                                        if num_match_clients == 0:
                                            if 'add' not in modify:
                                                modify.append('add')
                                                config_to_modify['addc'] = [items]
                                            else:
                                                if 'addc' not in config_to_modify:
                                                    config_to_modify['addc']= [items]
                                                else:
                                                    if items not in config_to_modify['addc']:
                                                        config_to_modify['addc'].append(items)
                                    
                                    elif key == 'referrals':
                                        
                                        for config in obj_config['export'][key]:
                                            if items['referral'] == config['referral']:
                                                num_match_referrals = num_match_referrals + 1
                                                if items['remote-servers'] == config['remote-servers']:
                                                    if items['remote-path'] == config['remote-path']:
                                                        pass
                                                    else:
                                                        if 'mod' not in modify:
                                                            modify.append('mod')
                                                            config_to_modify['modr'] = [items]
                                                        else:
                                                            if 'modr' not in config_to_modify:
                                                                config_to_modify['modr'] = [items]
                                                            else:
                                                                if items not in config_to_modify['modr']:
                                                                    config_to_modify['modr'].append(items)
                                                                
                                                            
                                                else:
                                                    if 'mod' not in modify:
                                                        modify.append('mod')
                                                        config_to_modify['modr'] = [items]
                                                    else:
                                                        if 'modr' not in config_to_modify:
                                                            config_to_modify['modr'] = [items]
                                                        else:
                                                            if items not in config_to_modify['modr']:
                                                                config_to_modify['modr'].append(items)       

                                        if num_match_referrals == 0:        
                                            if 'add' not in modify:
                                                modify.append('add')
                                                config_to_modify['addr'] = [items]
                                            else:
                                                if 'addr' not in config_to_modify:
                                                    config_to_modify['addr'] = [items]
                                                else:
                                                    config_to_modify['addr'].append(items)
                                
                                else:
                                    if key == 'clients':
                                        if 'add' not in modify:
                                            modify.append('add')
                                            config_to_modify['addc'] = [items]
                                        else:
                                            if 'addc' not in config_to_modify:
                                                config_to_modify['addc']= [items]
                                            else:
                                                if items not in config_to_modify['addc']:
                                                    config_to_modify['addc'].append(items)
                                    
                                    elif key == 'referrals':
                                        if 'add' not in modify:
                                            modify.append('add')
                                            config_to_modify['addr'] = [items]
                                        else:
                                            if 'addr' not in config_to_modify:
                                                config_to_modify['addr'] = [items]
                                            else:
                                                config_to_modify['addr'].append(items)
                            
                    else:
                        
                        for optionvalue in obj_config:
                            if key in optionvalue:
                                if value == optionvalue[key]:
                                    pass
                                else:
                                    if 'add' not in modify:
                                        modify.append('add')
                                    if 'add' not in config_to_modify:
                                        config_to_modify['add'] = []
                                    option_value = {key: value}
                                    if option_value not in config_to_modify['add']:
                                        config_to_modify['add'].append(option_value)

                

            else:

                if action == 'nfs_service':
                    if 'version' not in obj_config_tobe:
                        obj_config_tobe['version'] = '3'
                    # if 'restart' in obj_config_tobe:
                    #     if obj_config_tobe['restart']:
                    #         if 'restart' not in modify:
                    #             modify.append('restart')
                    #     else:
                    #         if 'add' not in modify:
                    #             modify.append('add')       
                    # else:
                    #     if 'add' not in modify:
                    #         modify.append('add')  
                    if 'version' not in config_to_modify:
                        config_to_modify['version'] = []
                    if key == 'version':
                        if obj_config_tobe['version'] == 'all':
                            for key, value in obj_config.items():
                                if 'Status' in key:
                                    if 'restart' in obj_config_tobe:
                                        if obj_config_tobe['restart']: 
                                            if value:
                                                if 'restart' not in modify:
                                                    modify.append('restart')
                                                
                                                config_to_modify['version'].append({'version': str(key[1])})
                                        else:
                                            if not value:
                                                if 'add' not in modify:
                                                    modify.append('add')
                                                config_to_modify['version'].append({'version': str(key[1])})
                                    else:
                                        if not value:
                                            if 'add' not in modify:
                                                modify.append('add')
                                            config_to_modify['version'].append({'version': key[1]})
                        else:
                            vstatuskey = 'v' + str(obj_config_tobe['version']) + 'Status'
                            
                            if vstatuskey in obj_config:
                                if not obj_config[vstatuskey]:
                                    
                                    if 'add' not in modify:
                                        
                                        modify.append('add')
                                        config_to_modify['version'].append({'version': obj_config_tobe['version']})                
                                        
        if 'new_export_name' in obj_config_tobe:
            modify.append('rename')

    else:
        for key, value in obj_config_tobe.items():
            if obj_key is not None:
                if key in mod_keys[obj_key]:     
                    if isinstance(value, list):  
                        for items in value:
                            num_match_clients = 0
                            num_match_referrals = 0
                            if isinstance(items, dict):
                                if key in obj_config['export']:
                                    for config in obj_config['export'][key]:
                                        if key == 'clients':
                                            
                                            if items['clientid'] == config['clientid']:
                                                if 'del' not in modify:
                                                    modify.append('del')
                                                    config_to_modify['delc'] = [items]
                                                else:
                                                    if 'delc' not in config_to_modify:
                                                        config_to_modify['delc'] = [items]
                                                    else:
                                                        config_to_modify['delc'].append(items)                                            
                                        elif key == 'referrals':
                                            if items['referral'] == config['referral']:
                                                if 'del' not in modify:
                                                    modify.append('del')
                                                    config_to_modify['delr'] = [items]
                                                else:
                                                    if 'delr' not in config_to_modify:
                                                        config_to_modify['delr'] = [items]
                                                    else:
                                                        if items not in config_to_modify['delr']:
                                                            config_to_modify['delr'].append(items)
                    else:
                        if 'del' not in modify:
                            modify.append('del')
                        if 'del' not in config_to_modify:
                            config_to_modify['del'] = []
                        option_value = {key: value}
                        if option_value not in config_to_modify['del']:
                            config_to_modify['del'].append(option_value)
            else:
                if action == 'nfs_service':
                    
                    if 'version' not in obj_config_tobe:
                        obj_config_tobe['version'] = '3'
                    
                    if 'version' not in config_to_modify:
                        config_to_modify['version'] = []

                    if obj_config_tobe['version'] == 'all':
                        for key, value in obj_config.items():
                            if 'Status' in key:
                                if value:
                                    if 'del' not in modify:
                                        modify.append('del')
                                    config_to_modify['version'].append({'version': str(key[1])})
                    else:
                        vstatuskey = 'v' + str(obj_config_tobe['version']) + 'Status'
                        if vstatuskey in obj_config:
                            if obj_config[vstatuskey]:
                                if 'del' not in modify:
                                    modify.append('del')
                                config_to_modify['version'].append({'version': str(obj_config_tobe['version'])})  
                    
        if 'destroy' in obj_config_tobe:
            if obj_config_tobe['destroy']:
                modify.append('destroy')
    
    return modify, config_to_modify


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


def nfs():
    conditions = dict(
        nfs_export=dict(query=dict(), req_key=['export'], opt_key=[], will_change=True, header=None),
		nfs_option=dict(query=dict(), req_key=['option'], opt_key=[], will_change=True, header=None),
		nfs_service=dict(query=dict(), req_key=[], opt_key=[], will_change=True, header=None)
		
       
    )

    cmd_templates = dict(nfs_export={
									'show': '["nfs export show detailed $name"]',
									'add': '["nfs export add $name"]',
									'del':   '["nfs export del $name"]',
									'mod': '["nfs export modify $name"]',
									'rename': '["nfs export rename $name $new_export_name"]',
									'destroy': '["nfs export destroy $name"]',
                                    'create': '["nfs export create $name"]'
									},                
						nfs_service={
									'show': '["/api/v2/dd-systems/0/protocols/nfs"]',
									'add': '["nfs enable"]',
									'del':   '["nfs disable"]',
									'restart': '["nfs restart"]'
									},
						nfs_option={
									'show': '["nfs option show "]',
									'add': '["nfs option set"]',
									'del':   '["nfs option reset"]',
									} 
						)

    return conditions, cmd_templates


def build_commands(modify, action, arg_dict, config_to_modify, obj_key, cmd_templates):
    commands = []
    for mod in modify:
        command_to_run = ''
        cmd = cmd_templates[action][mod]
        
        if len(cmd) > 0:
            command_template = Template(cmd)
            
            if mod == 'mod' or mod == 'add' or mod == 'del':
                if obj_key is not None:
                    for key, value in config_to_modify.items():  
                        if key.startswith(mod):
                            for val in value:
                                command = eval(command_template.substitute(**arg_dict[obj_key]))
                                if mod != 'del':
                                    for ky, vy in val.items():
                                        if ky == 'clientid':
                                            ky = 'clients'
                                        command.append(ky)
                                        command.append(vy) 
                                else:
                                    for ky, vy in val.items():
                                        if ky == 'clientid' or ky == 'referral':
                                            if ky == 'clientid':
                                                ky = 'clients'
                                            elif ky == 'referral':
                                              ky = 'referrals'
                                            command.append(ky)
                                            command.append(vy) 
                                        else:
                                          command.append(ky)
                                          # command.append(vy)
                                command_to_run = ''
                                for arg in command:
                                    command_to_run = str(command_to_run + " " + str(arg)).strip()
                                # print(command_to_run.strip())
                                if command_to_run not in commands:
                                    command_to_run = command_to_run.replace('[', '').replace("'", '').replace(']', '').strip()
                                    commands.append(command_to_run)
                else:
                    for key, value in config_to_modify.items():
                        for val in value:
                            command = eval(command_template.substitute(**arg_dict))
                            for ky, vy in val.items():
                                command.append(ky)
                                command.append(vy)
                            command_to_run = ''
                            for arg in command:
                                command_to_run = str(command_to_run + " " + str(arg)).strip()
                            # print(command_to_run.strip())
                            if command_to_run not in commands:
                                command_to_run = command_to_run.replace('[', '').replace("'", '').replace(']', '').strip()
                                commands.append(command_to_run)
                   
            elif mod == 'create':
                config_to_modify = {}
                modify = []
                command = eval(command_template.substitute(**arg_dict[obj_key]))
                for key, value in arg_dict[obj_key].items():
                    if key != 'state' and key != 'name':
                        if not isinstance(value, list):
                            command.append(key)
                            command.append(value)
                        else:
                            if len(value) > 1:
                                items = value[1:]
                                k = 'add' + key[0]
    
                                for v in items:
                                    if 'add' not in modify:
                                        modify.append('add')
                                        if k not in config_to_modify:
                                            config_to_modify[k] = [v]
                                    else:
                                        if k not in config_to_modify:
                                            config_to_modify[k] = [v]
                                        else:
                                            config_to_modify[k].append(v)
                            
                            
                            for ky, vy in value[0].items():
                                if ky == 'clientid':
                                    ky = 'clients'
                                command.append(ky)
                                command.append(vy)

                for arg in command:
                    command_to_run = command_to_run + " " + str(arg)
                if command_to_run not in commands:
                    command_to_run = command_to_run.replace('[', '').replace("'", '').replace(']', '').strip()
                    commands.append(command_to_run)
                commands = commands + build_commands(modify, action, arg_dict, config_to_modify, obj_key, cmd_templates)
            elif mod == 'show':
                if obj_key is not None:
                    command = eval(command_template.substitute(**arg_dict[obj_key]))
                else:
                    command = eval(command_template.substitute(**arg_dict))
                for arg in command:
                    command_to_run = command_to_run + " " + str(arg)
                if command_to_run not in commands:
                    command_to_run = command_to_run.replace('[', '').replace("'", '').replace(']', '').strip()

                    commands.append(command_to_run)
            else:
                if obj_key is not None:
                    command = eval(command_template.substitute(**arg_dict[obj_key]))
                    for arg in command:
                        command_to_run = command_to_run + " " + str(arg)
                    if command_to_run not in commands:
                        command_to_run = command_to_run.replace('[', '').replace("'", '').replace(']', '').strip()

                    commands.append(command_to_run)
                else:
                    command = eval(command_template.substitute(**arg_dict))
                    for key in config_to_modify:
                        
                        for val in config_to_modify[key]:
                            command = eval(command_template.substitute(**arg_dict))
                            for ky, vy in val.items():
                                command.append(ky)
                                command.append(vy)
                            command_to_run = ''
                            for arg in command:
                                command_to_run = str(command_to_run + " " + str(arg)).strip()
                            # print(command_to_run.strip())
                            if command_to_run not in commands:
                                command_to_run = command_to_run.replace('[', '').replace("'", '').replace(']', '').strip()
                                commands.append(command_to_run)
                   
                
    return commands      


def get_obj_key(arg_dict, obj_keys):
    for obj in obj_keys:
        if obj in arg_dict:
            return obj
            break


def change_object(server, user, password, command=None, endpoint=None):
    port = 22
    if command is not None:
        cmd_output = dd_connect.dd_ssh(server, user, port, command, private_key=None, password=password, header=None)
        # jsonout = nfs_output(output=cmd_output['output'])
        if not cmd_output['failed']:
            return [True, cmd_output['output']]
        else:
            return [False, cmd_output['output']]


def main():

  conditions, cmd_templates = nfs()
  fields = {
      'state': {'type': 'str', 'choices': ['present', 'absent'], 'required': True},
      'restart': {'type': 'bool'},
      'version': {'type': 'str'},
      'export': {'type': 'dict', 'required': False,
                  'options': {'name': {'type': 'str'}, 'path': {'type': 'str'}, 'destroy': {'type': 'bool'}, 'new_export_name': {'type': 'str'},
                              'clients': {'type': 'list', 'suboptions': {
                                          'clientid': {'type': 'str'}, 'options': {'type': 'str'}

                                          }
                                },
                              'referrals': {'type': 'list', 'suboptions': {
                                          'referral': {'type': 'str'}, 'remote-servers': {'type': 'str'}, 'remote-path': {'type': 'str'}

                                          }
                                }

                  }
        },
      
      'option': {'type': 'dict', 'required': False, 'suboptions': {
        'default-export-version': {'type': 'str'},
        'default-server-version': {'type': 'str'},
        'nfs4-grace-period': {'type': 'str'},
        'nfs4-lease-interval': {'type': 'str'},
        'mountd-port': {'type': 'str'},
        'nfs4-port': {'type': 'str'},
        'nfs3-port': {'type': 'str'},
        'nfs4-domain': {'type': 'str'},
        'nfs4-idmap-out-numeric': {'type': 'str'},
        'nfs4-idmap-active-directory': {'type': 'str', 'choices': ['enabled', 'disabled']},
        'nfs4-acls': {'type': 'str', 'choices': ['enabled', 'disabled']},
        'default-root-squash': {'type': 'str', 'choices': ['enabled', 'disabled']},
        'force-minimum-root-squash-default': {'type': 'str', 'choices': ['enabled', 'disabled']},
        'report-mtree-quota': {'type': 'str', 'choices': ['enabled', 'disabled']},
      }
      },
  
      'host': {'type': 'str', 'required': True},
      'port': {'type': 'int', 'default': 22},
      'username': {'type': 'str', 'required': True},
      'private_key': {'type': 'str', 'no_log': True},
      'password': {'type': 'str', 'no_log': True},
  }


  module = AnsibleModule(argument_spec=fields, mutually_exclusive=[('private_key', 'password')],
                          required_one_of=[('private_key', 'password')])
  
  server = module.params['host']
  user = module.params['username']
  port = module.params['port']
  private_key = module.params['private_key']
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

  failed_cmd_out = 'was not found'
  str_list_to_remove = []
  obj_keys = ['export', 'option']
  modify_keys = {'export': ['clients', 'referrals'], 'option': ['default-export-version', 'default-server-version', 'nfs4-grace-period', 'nfs4-lease-interval', 'mountd-port', 'nfs4-port', 'nfs3-port', 'nfs4-domain', 'nfs4-idmap-out-numeric', 'nfs4-idmap-active-directory', 'nfs4-acls', 'default-root-squash', 'force-minimum-root-squash-default', 'report-mtree-quota']}
  obj_key = get_obj_key(arg_dict, obj_keys)
  action = condition_check(conditions, command_build_dict=arg_dict)
  modify = ['show']

  if len(action) > 0:
    headers = None
    commands = build_commands(modify, action, arg_dict, modify_keys, obj_key, cmd_templates)
    command = commands[0]
    if command.startswith('/'):
        obj_exist, obj_config = check_if_object_present_absent(server, user, password, command=None, endpoint=command, failed_cmd_out=failed_cmd_out, headers=headers)
    else:
        obj_exist, obj_config = check_if_object_present_absent(server, user, password, command=command, endpoint=None, failed_cmd_out=failed_cmd_out, headers=headers)
    
    if obj_exist:
      modify, config_to_modify = check_if_modify_required(action, arg_dict, obj_key, obj_config=obj_config, mod_keys=modify_keys ,command=None, endpoint=None)
      
      if len(modify) > 0:
        commands = build_commands(modify, action, arg_dict, config_to_modify, obj_key, cmd_templates)

        if len(commands) > 0:
          cmd_combined_out = []
          for command in commands:
            status, output = change_object(server, user, password, command=command, endpoint=None)
            status = 'SUCCESS' if status else 'FAILED'
            cmd_combined_out.append({'status': status, 'output': output})
            if not status:
              cmd_output['failed'] = True
              break 
            else:
              cmd_output['failed'] = False
          cmd_output['output'] = cmd_combined_out
          cmd_output['changed'] = True
        else:
            cmd_output['output'] = obj_config
            cmd_output['failed'] = False
            cmd_output['changed'] = False
      
      else:
          cmd_output['output'] = obj_config
          cmd_output['failed'] = False
          cmd_output['changed'] = False
  
    else:  
      if arg_dict['state'] == 'present':
        modify = ['create']
        commands = build_commands(modify, action, arg_dict, modify_keys, obj_key, cmd_templates)
        cmd_combined_out = []
        if len(commands) > 0:
          for command in commands:
            status, output = change_object(server, user, password, command=command, endpoint=None)
            status = 'SUCCESS' if status else 'FAILED'
            cmd_combined_out.append({'status': status, 'output': output})
            if not status:
              cmd_output['failed'] = True
              break 
            else:
              cmd_output['failed'] = False
          cmd_output['output'] = cmd_combined_out
          cmd_output['changed'] = False


      else:
        cmd_output['output'] = 'Configuration Item does not exist. No Action is needed.'
        cmd_output['changed'] = False
        cmd_output['failed'] = False

  else:
    cmd_output['output'] = "As per playbook condition, no action matched. Please re-check documentation and rerun the playbook"
    cmd_output['failed'] = True
    cmd_output['changed'] = False

  module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=cmd_output['changed'])

if __name__ == '__main__':
  main()