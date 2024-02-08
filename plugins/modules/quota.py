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
module: mtree
short_description: This module enables you to manage quotas on mtrees, storage units..
version_added: "1.0.0"
description: The quota command lets you modify the amount of storage space for MTrees and for VTL and DD Boost storage units. 
  
options:
state:
  type: str
  choices:
  - present
  - absent
  description: Choose one of the option.
  required: true
capacity:
  type: dict
  description:  There are two quota limits - hard and soft. The hard limit prevents writes from exceeding the quota.
  options:
    mtrees: 
      type: list
      description: List of Mtrees to configure quota
      required: false
    soft-limit:
      type: str
      description: Soft limit for the size. Value for this parameter must be in format <n> MiB|GiB|TiB|PiB e.g. 10 GiB
      required: false
    hard-limit:
      type: str
      required: false
      description: Hard limit for the size. Value for this parameter must be in format <n> MiB|GiB|TiB|PiB e.g. 10 GiB
streams:
  type: dict
  description: Set/Reset Streams quota
  options:
    storage_unit:
      type: str
      required: false
      description: Type the Storage Unit name to modify Streams quota. One Storage Unit at time. 
    write-stream-soft-limit:
      type: str
      required: false
      description: Set Write streams soft limit. Value to this parameter must be in format <n> e.g. 100
    read-stream-soft-limit:
      type: str
      required: false
      description: Set read streams soft limit. Value to this parameter must be in format <n> e.g. 100
    repl-stream-soft-limit:
      type: str
      required: false
      description: Set replication streams soft limit. Value to this parameter must be in format <n> e.g. 100
    combined-stream-soft-limit:
      type: str
      required: false
      description: Set Read/Write/Repl streams soft limit. Value to this parameter must be in format <n> e.g. 100
    combined-stream-hard-limit:
      type: str
      required: false
      description: Set Read/Write/Repl streams hard limit. Value to this parameter must be in format <n> e.g. 100

author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
	- name: Enable capacity quota
		dellemc.datadomain.quota:
			state: present

	- name: Disable capacity quota
		dellemc.datadomain.quota:
			state: absent			
	
	- name: Set capacity quota limits for mtrees
		dellemc.datadomain.quota:
			state: present
            capacity:
                mtrees:
                    - /data/col1/mtreepath01
                    - /data/col1/mtreepath02
                soft-limit: 10 GiB
                hard-limit: 10 GiB
	
	- name: Reseet capacity quota limits for mtrees to default values (none)
		dellemc.datadomain.quota:
			state: absent
            capacity:
                mtrees:
                    - /data/col1/mtreepath01
                    - /data/col1/mtreepath02
                soft-limit: 10 GiB 
                hard-limit: 10 GiB


	- name: Set streams quota limits for Storage units. 
		dellemc.datadomain.quota:
			state: present
            streams:
                storage_unit: mtreepath01
                write-stream-soft-limit: 10
                read-stream-soft-limit: 10
                repl-stream-soft-limit: 100
                combined-stream-soft-limit: 1000
                combined-stream-hard-limit: 1000
	
	- name: Reset streams quota limits for Storage units to default values . 
		dellemc.datadomain.quota:
			state: present
            streams:
                storage_unit: mtreepath01
                write-stream-soft-limit: 10
                read-stream-soft-limit: 10
                repl-stream-soft-limit: 100
                combined-stream-soft-limit: 1000
                combined-stream-hard-limit: 1000
'''

def quota():
    condition = dict(
        quota_streams=dict(query=dict(), req_key=['streams'], opt_key=[], will_change=True, header=None),
        quota_capacity=dict(query=dict(), req_key=['capacity'], opt_key=[], will_change=True, header=None),
        quota_service=dict(query=dict(), req_key=[], opt_key=[], will_change=True, header=None)
    )

    cmd_templates = dict(quota_service={
        'show':'["quota capacity status"]',
        'enable':'["quota capacity enable"]',
        'disable':'["quota capacity disable"]'
    },
    quota_capacity={
        'enable':'["quota capacity enable"]',
        'show':'["quota capacity show mtrees $mtrees"]',
        'set':'["quota capacity set mtrees $mtrees"]',
        'reset':'["quota capacity reset mtrees $mtrees"]'
    },
        quota_streams={
        'show':'["quota streams show storage-unit $storage_unit"]',
        'set':'["quota streams set storage-unit $storage_unit"]',
        'reset':'["quota streams reset storage-unit $storage_unit"]'
    }
    )
    return condition, cmd_templates


def get_obj_key(arg_dict, obj_keys):
    for obj in obj_keys:
        if obj in arg_dict:
            return obj
            break


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


def build_commands(modify, action, arg_dict, obj_key, cmd_templates):
    commands = {}
    payload = {}
    if obj_key is None:
        obj_key = []
    if len(obj_key) > 0:
        narg_dict = copy.deepcopy(arg_dict[obj_key])
    else:
        narg_dict = copy.deepcopy(arg_dict)
    keys_to_remove = ['state', 'port']

    for mod in modify:
        command_to_run = ''
        cmd = cmd_templates[action][mod]
        # if mod == 'show':
        command_to_run = ''
        command_template = Template(cmd)
        command = eval(command_template.substitute(**narg_dict))
        mod_to_check = ['show', 'enable', 'disable']
        if obj_key is not None and mod not in mod_to_check:
            key_to_check = ['mtrees', 'storage_unit']
            for key, value in narg_dict.items():
                if key not in key_to_check:
                    if mod == 'reset':
                        command.append(key)
                    else:
                        command.append(key)
                        command.append(value)
        for arg in command:
            command_to_run = command_to_run + " " + str(arg)
                    
        if command_to_run not in commands:
            command_to_run = command_to_run.replace('[', '').replace("'", '').replace(']', '').strip()
            commands[mod] = command_to_run

    return commands, payload      


def get_quota_details(output, obj_key=None):
    if obj_key == 'capacity':
        headers = ['mtrees', 'pre-compGiB', 'soft-limit', 'hard-limit']
    elif obj_key == 'streams':
        headers = ['storage_unit', 'write-stream-soft-limit', 'read-stream-soft-limit', 'repl-stream-soft-limit', 'combined-stream-soft-limit', 'combined-stream-hard-limit']
    else:
        headers = None

    final_data = {}
    cmd_out = output.strip().split('\n')
    dash_count = 0

    if len(cmd_out) == 1:
        status = True if 'enabled' in str(cmd_out[0]) else False
        final_data['status'] = status
        final_data['output'] = [cmd_out[0]]
    else:
        if 'Quota Capacity is disabled' in str(output):
            final_data['status'] = False
            final_data['output'] = []
        else:
            final_data['status'] = True
            final_data['output'] = []
    for line in cmd_out:
        if '--' in line and 'Soft-Limit' not in line:
            dash_count = dash_count + 1
        if '--' not in line and len(line.strip()) > 0 and dash_count == 1:
            obj = re.split('\\s\\s\\s+', line)
            if dash_count > 1:
                break
            if headers is not None:
                i = 0
                data_dict = {}
                for h in headers:
                    data_dict[h] = obj[i]
                    i = i + 1
                final_data['output'].append(data_dict)

    return final_data


def check_if_object_present_absent(server, user, password, obj_key=None, command=None, endpoint=None, failed_cmd_out=None, headers=None):
    port = 22
    if command is not None:
        cmd_output = dd_connect.dd_ssh(server, user, port, command, private_key=None, password=password, header=None)
        jsonout = get_quota_details(output=cmd_output['output'],obj_key=obj_key)
        status_code = True
        if 'status' not in str(command):
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
        else:
            return [True, jsonout]
    elif endpoint is not None:
        cmd_output = dd_connect.dd_requests(server, user, api_pass=password, endpoint=endpoint, request_type='get', payload=None, query_params=None, field_params=None)
        if not cmd_output['failed']:
            return [True,  cmd_output['output']]
        else:
            return [False,  cmd_output['output']]


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
    
    if obj_key is None:
        status = obj_config['status']
        if status and arg_dict['state'] == 'present':
            pass
        elif status and arg_dict['state'] == 'absent':
            if 'disable' not in modify:
                modify.append('disable')
        elif not status and arg_dict['state'] == 'present':
            if 'enable' not in modify:
                modify.append('enable')
        elif not status and arg_dict['state'] == 'absent':
            pass
    else:
        
        if obj_key == 'capacity':
            key_to_lookup = 'mtrees'
        else:
            key_to_lookup = 'storage_unit'
        if arg_dict['state'] == 'present':
            if not obj_config['status']:
                if 'enable' not in modify:
                    modify.append('enable')
                else:
                    pass
            
            for config in obj_config['output']:
                if isinstance(temp_req_config[key_to_lookup], list):
                    if config[key_to_lookup] in temp_req_config[key_to_lookup]:
                        check_status = True
                    else: 
                        check_status = False
                else:
                    if config[key_to_lookup] == temp_req_config[key_to_lookup]:
                        check_status = True
                    else: 
                        check_status = False
                    
                if check_status:
                    for key, value in config.items():
                        if key != key_to_lookup:
                            value_to_check = ''
                            if key in temp_req_config:
                                if obj_key == 'capacity':
                                    value_to_check = convert_to_MiB(temp_req_config[key])
                                else:
                                    value_to_check =temp_req_config[key]
                                if value == 'none':
                                    value = 0
                                
                                if int(value) == int(value_to_check):
                                    pass
                                else:
                                    if 'set' not in modify:
                                        modify.append('set')
                                    if 'set' not in config_to_modify:
                                        config_to_modify['set'] = []
                                    config_to_modify['set'].append({key: temp_req_config[key]})
            
        else:
            for key in temp_req_config:
                if 'reset' not in modify:
                    modify.append('reset')
                if 'reset' not in config_to_modify:
                    config_to_modify['reset'] = []
                if key == 'mtrees':
                    config_to_modify['reset'].append({key: temp_req_config[key]})
                else:
                    config_to_modify['reset'].append(key)
        
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


def convert_to_MiB(size):
    conversion_dict = {'MiB': '0', 'GiB': '1', 'TiB': '2', 'PiB': '3'}
    num, unit = size.split(' ')
    multiplier = conversion_dict[unit] if conversion_dict[unit] != 0 else 1
    size_in_mib = int(num.strip()) * 1024 ** int(multiplier)

    return size_in_mib


def main():
    fields = {'state': {'type': 'str', 'choices': ['present', 'absent'], 'required': True},
            'capacity': {'type': 'dict', 'options':  {'mtrees': {'type': 'list', 'required': False},
                        'soft-limit': {'type': 'str', 'required': False}, 'hard-limit': {'type': 'str', 'required': False}}
                        },
    'streams': {'type': 'dict', 'options':  {'storage_unit': {'type': 'str', 'required': False},
				'write-stream-soft-limit': {'type': 'str', 'required': False}, 
				'read-stream-soft-limit': {'type': 'str', 'required': False},
				'repl-stream-soft-limit': {'type': 'str', 'required': False},
				'combined-stream-soft-limit': {'type': 'str', 'required': False}, 
				'combined-stream-hard-limit': {'type': 'str', 'required': False}}
                },
		'host': {'type': 'str', 'required': True},
    'port': {'type': 'int', 'default': 22},
    'username': {'type': 'str', 'required': True},
    'private_key': {'type': 'str', 'no_log': True},
    'password': {'type': 'str', 'no_log': True},
    }
    module = AnsibleModule(argument_spec=fields, mutually_exclusive=[('private_key', 'password'), ('capacity', 'streams')],
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
    conditions, cmd_templates = quota()
    failed_cmd_out = ['No such file or directory', 'not found']
    cmd_output = {}
    obj_keys = ['capacity', 'streams']
    obj_key = get_obj_key(arg_dict, obj_keys)
    headers = []
    action = condition_check(conditions, command_build_dict=arg_dict)
    modify = ['show']
    if len(action) > 0:
        headers = None
        commands, payload = build_commands(modify, action, arg_dict, obj_key, cmd_templates)
        obj_config = {}
        if len(commands) > 0:
            cmd_combined_out = []
            obj_exist, obj_config = check_if_object_present_absent(server, user, password, obj_key=obj_key, command=commands[modify[0]], endpoint=None, failed_cmd_out=failed_cmd_out, headers=None)
            if obj_exist:
                modify, config_to_modify = check_if_modify_required(arg_dict, obj_key, obj_config)
                if len(modify) > 0:
                    commands, payload = build_commands(modify, action, arg_dict, obj_key, cmd_templates)    
                    if len(commands) > 0:
                        cmd_combined_out = []
                        for key in commands:
                            command = commands[key]
                            status, output = change_object(server, user, password, command=command, endpoint=None, request_type=None, payload=None)
                            status = 'SUCCESS' if status else 'FAILED'
                            cmd_combined_out.append({'status': status, 'output': output})
                            if status != 'SUCCESS':
                                cmd_output['failed'] = True
                                break 
                            else:
                                cmd_output['failed'] = False
                                cmd_output['output'] = cmd_combined_out
                                cmd_output['changed'] = True   

                else:
                    cmd_output['output'] = obj_config
                    cmd_output['changed'] = False
                    cmd_output['failed'] = False
            else:
                cmd_output['output'] = obj_config
                cmd_output['failed'] = False
                cmd_output['changed'] = False
    else:
        cmd_output['output'] = 'Please check the input parameters and rerun the playbook.'
        cmd_output['failed'] = False
        cmd_output['changed'] = False
    module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=cmd_output['changed'])


if __name__ == '__main__':
    main()