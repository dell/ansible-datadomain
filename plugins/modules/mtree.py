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
module: nfs
short_description: This module enables you to add NFS clients and manage access to a protection system..
version_added: "1.0.0"
description: This module enables you to add NFS clients and manage access to a protection system.
  
options:
state:
  type: str
  choices:
  - present
  - absent
  required: true
  description: Choose the option from the choices above
mtree_path:
  type: str
  required: true
  description: The format of the mtree-path is /data/col1/mtreename. Naming conventions for creating MTrees include uppercase and lowercase letters (A-Z, a-z), numbers 0-9, single, non-leading embedded space, exclamation point, hash, dollar sign, ampersand, caret, tilde, left and right parentheses, left and right brackets, left and right braces (!, \#, $, &, ^, ~, (), [], {}). The maximum length for an MTree name is 50 characters. 
new_mtree_path:
  type: str
  required: false
  description: New mtree path to rename the existing mtree.
tenant-unit:
  type: str
  required: false
  description: The name of the tenant-unit you want to associate with the MTree.
option:
  type: dict
  description: Set\Reset Oracle Optimized Deduplication on the specified MTree.
  options:
    app-optimized-compression:
      type: str
      choices:
      - none
      - global
      - oracle1
      required: true
      description: Set\Reset Oracle Optimized Deduplication on the specified MTree.

author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
	- name: Create a MTree
		dellemc.datadomain.mtree:
			state: present
			mtree_path: /data/col1/mtreepath
			tenant-unit: backup # optional paramemter. To assign quota use quota module.
	
	
	- name: Rename a MTree
		dellemc.datadomain.mtree:
			state: present
			mtree_path: /data/col1/mtreepath
			new_mtree_path: /data/col1/mtreepath01


	- name: Undelete a MTree
		dellemc.datadomain.mtree:
			state: present
			mtree_path: /data/col1/mtreepath	# If mtree is in "D" status, it will undelete it, if mtree does not exist, it will create it, else not action taken.


	- name: Delete a MTree if exists.
		dellemc.datadomain.mtree:
			state: absent
			mtree_path: /data/col1/mtreepath
			
	- name: Assign MTree to tenant-unit
		dellemc.datadomain.mtree:
			state: present
			mtree_path: /data/col1/mtreepath
			tenant-unit: backup

	- name: Unassign MTree to tenant-unit
		dellemc.datadomain.mtree:
			state: present
			mtree_path: /data/col1/mtreepath
			tenant-unit: ''

	- name: Reset app-optimized-compression algo to default for the MTree
		dellemc.datadomain.mtree:
			state: present
			mtree_path: /data/col1/mtreepath
			option:
				app-optimized-compression: global #This will run reset command to set option to default value.


	- name: Set app-optimized-compression algo to default for the MTree
		dellemc.datadomain.mtree:
			state: present
			mtree_path: /data/col1/mtreepath
			option:
				app-optimized-compression: global 
'''

def mtree():
    conditions = dict(
		mtree_service=dict(query=dict(), req_key=[], opt_key=[], will_change=True, header=None)
		
       
    )

    cmd_templates = dict(mtree_service={
									'show':{'default': '["mtree list $mtree_path"]', 'option': '["mtree option show mtree $mtree_path"]'},
									'del': '["/rest/v1.0/dd-systems/0/mtrees/$mtree_path"]',
                                    'reset': {'option': '["mtree option reset"]'},
									'mod': '["mtree modify $mtree_path"]',
									'reset': '["mtree option reset"]',
									'set': '["mtree option set"]',
									'rename': '["mtree rename $mtree_path"]',
									'undel': '["mtree undelete $mtree_path"]',
                                    'create': '["mtree create $mtree_path"]',
                  'create': '["mtree create $mtree_path"]'
									}, 
						
						)

    return conditions, cmd_templates


def check_if_object_present_absent(server, user, password, command=None, endpoint=None, failed_cmd_out=None, headers=None):
    port = 22
    if command is not None:
        cmd_output = dd_connect.dd_ssh(server, user, port, command, private_key=None, password=password, header=None)
        if 'option' in command or 'list' in command:
            mtree_path = command.split(' ')[-1]
            jsonout = get_mtree_options(output=cmd_output['output'],obj_key=None, mtree_path=mtree_path,  headers=headers)
        else:
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


def get_obj_key(arg_dict, obj_keys):
    for obj in obj_keys:
        if obj in arg_dict:
            return obj
            break


def get_mtree_options(output,obj_key=None, mtree_path=None, headers=None):
    final_data = {}
    cmd_out = output.split('\n')
    for line in cmd_out:
        if '--' not in line and len(line.strip()) > 0:
            obj = re.split('\\s\\s\\s+', line)
            if obj[0] == mtree_path:
                if headers is not None:
                    i = 0
                    for h in headers:
                        final_data[h] = obj[i]
                        i = i + 1
                else:
                    if '(none)' in obj[2]:
                        obj[2] = obj[2].split(' ')[0]
                    final_data[obj[1]] = obj[2]
    return final_data


def check_if_modify_required(arg_dict, obj_key, obj_config, mod_keys=None, command=None, endpoint=None, diff_config_command_keys=None):
    modify = []
    config_to_modify = {}
    
    future_config = copy.deepcopy(arg_dict)
    keys_to_remove = ['state', 'port']
    for key in keys_to_remove:
        if key in future_config:
            try:
                del future_config[key]
            except KeyError:
                pass
    if obj_key is None:
        obj_key = []
    keys_to_check = ['state', 'port']
    if arg_dict['state'] == 'present': 
        for key, value in arg_dict.items():
            if key not in keys_to_check:
                # if obj_key is not None:
                if key in obj_key:
                    if key in obj_config:
                        for k, v in value.items():
                            if k in obj_config[key]:
                                if v == obj_config[key][k]:
                                    pass
                                else:
                                    if 'set' not in modify:
                                        modify.append('set') 
                                        if 'set' not in config_to_modify:
                                            config_to_modify['set'] = {}
                                            config_to_modify['set'][key] = {}
                                    else:
                                        if key not in config_to_modify['set']:
                                            config_to_modify['set'][key] = {}
                                    config_to_modify['set'][key][k] = value[k]
                            else:
                                pass
                
                else:
                    if obj_config['default']['status'] == 'D':
                        if 'undel' not in modify:
                            modify.append('undel') 
                        if 'undel' not in config_to_modify:
                            config_to_modify['undel'] = {}
                        config_to_modify['undel']['mtree_path'] = obj_config['default']['mtree_path']
                    if key == 'new_mtree_path':
                        if 'rename' not in modify:
                            modify.append('rename') 
                        if 'rename' not in config_to_modify:
                            config_to_modify['rename'] = {}
                        config_to_modify['rename'][key] = value    
                    if key == 'tenant-unit':
                        if 'mod' not in modify:
                                modify.append('mod')
                        if 'mod' not in config_to_modify:
                            config_to_modify['mod'] = {}
                            
                        config_to_modify['mod'][key] = value

            else:
                pass

    else:
        if len(future_config) == 1:
            if obj_config['default']['status'] != 'D':
                if 'del' not in modify:
                    modify.append('del') 
                if 'del' not in config_to_modify:
                    config_to_modify['del'] = {}
                config_to_modify['del']['mtree_path'] = obj_config['default']['mtree_path']
        else:
            for key, value in arg_dict.items():
                if key not in keys_to_check:
                    # if obj_key is not None:
                    if key in obj_key:
                        if key in obj_config:
                            for k in value:
                                if k in obj_config[key]:                                   
                                    if 'reset' not in modify:
                                        modify.append('reset') 
                                        if 'reset' not in config_to_modify:
                                            config_to_modify['reset'] = {}
                                            config_to_modify['reset'][key] = {}
                                    else:
                                        if key not in config_to_modify['reset']:
                                            config_to_modify['reset'][key] = {}
                                    config_to_modify['reset'][key][k] = ''
                                        
                                else:
                                    pass
                    
                    else:
                        if key == 'tenant-unit':
                            if 'mod' not in modify:
                                    modify.append('mod')
                            if 'mod' not in config_to_modify:
                                config_to_modify['mod'] = {}
                                
                            config_to_modify['mod'][key] = 'none'  

                else:
                    pass

        
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


def build_commands(modify, action, arg_dict, config_to_modify, obj_key, cmd_templates):
    
    commands = {}
    payload = {}
    if obj_key is None:
        obj_key = []
    narg_dict = copy.deepcopy(arg_dict)
    for mod in modify:
        command_to_run = ''
        cmd = cmd_templates[action][mod]
        commands_to_work = {}
        if isinstance(cmd, dict):
            for key, value in cmd.items():
                if "default" not in key:
                    if key in narg_dict:
                        commands_to_work[key] = value
                else:
                    commands_to_work[key] = value
            
        else:
            commands_to_work[mod] = cmd

        if len(commands_to_work) > 0:
            if mod == 'show':
                for key, value in commands_to_work.items():
                    if eval(value)[0].startswith('/'):
                        narg_dict['mtree_path'] = narg_dict['mtree_path'].replace('/', '%2F')
                    else:
                        narg_dict['mtree_path'] = arg_dict['mtree_path']
                    command_to_run = ''
                    command_template = Template(value)
                    command = eval(command_template.substitute(**narg_dict))
                    
                    for arg in command:
                        command_to_run = command_to_run + " " + str(arg)
                        
                    if command_to_run not in commands:
                        command_to_run = command_to_run.replace('[', '').replace("'", '').replace(']', '').strip()
                        commands[key] = command_to_run
            else:
                
                for key, value in commands_to_work.items():
                    if eval(value)[0].startswith('/'):
                        narg_dict['mtree_path'] = narg_dict['mtree_path'].replace('/', '%2F')
                    else:
                        narg_dict['mtree_path'] = arg_dict['mtree_path']
                    command_to_run = ''
                    command_template = Template(value)
                    command = eval(command_template.substitute(**narg_dict))
                    for k, v in config_to_modify[mod].items():
                        if k in obj_key:
                            for ko, vo in config_to_modify[mod][k].items():
                                command.append(ko)
                                command.append(vo) 
                                command.append('mtree')
                                command.append(arg_dict['mtree_path']) 
                        elif len(v) > 0:
                            if mod != 'del':
                                if "create" in mod:
                                    command = command
                                    if 'tenant-unit' in arg_dict:
                                        if k == 'tenant-unit':
                                            command.append(k)
                                            command.append(v)
                                elif "undel" in mod:
                                    command = command
                                elif 'rename' in mod:
                                    command.append(v)  
                                else:
                                    command.append(k)
                                    command.append(v)
                            #Command giving mtree_path key in create
                        else:
                            command.append(k) 

                    for arg in command:
                        command_to_run = command_to_run + " " + str(arg)
                        
                    if command_to_run not in commands:
                        command_to_run = command_to_run.replace('[', '').replace("'", '').replace(']', '').strip()
                        commands[key] = command_to_run
        else:
            pass
    return commands, payload      


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
  conditions, cmd_templates = mtree()
  fields = {
     'state': {'type': 'str', 'choices': ['present', 'absent'], 'required': True},
    'mtree_path': {'type': 'str', 'required': True},
    'new_mtree_path': {'type': 'str', 'required': False},
    'tenant-unit': {'type': 'str', 'required': False},
    'option': {'type': 'dict', 'options': {'app-optimized-compression': {'type': 'str', 'choices': ['none', 'global', 'oracle1'], 'required': True}}},
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

  failed_cmd_out = 'no MTrees configured'
  cmd_output = {}
  str_list_to_remove = []
  diff_config_command_keys = ['option']
  # modify_keys = {'option': ['app-optimized-compression'], 'quota_config': ['soft_limit', 'hard_limit']}
  obj_keys, modify_keys = ['option'], []
  obj_key = get_obj_key(arg_dict, obj_keys)
  headers = []
  action = condition_check(conditions, command_build_dict=arg_dict)
  modify = ['show']

  if len(action) > 0:
    headers = None
    commands, payload = build_commands(modify, action, arg_dict, modify_keys, obj_key, cmd_templates)
    obj_config = {}
    if len(commands) > 0:
        if commands['default'].startswith('/'):
            obj_exist, config = check_if_object_present_absent(server, user, password, command=None, endpoint=commands['default'], failed_cmd_out=failed_cmd_out, headers=headers)
        else:
            if 'list' in commands['default']:
                headers = ['mtree_path', 'pre-comp', 'status']        
            obj_exist, config = check_if_object_present_absent(server, user, password, command=commands['default'], endpoint=None, failed_cmd_out=failed_cmd_out, headers=headers)   
        modify = []
        if obj_exist:
            obj_config['default'] = config
            for key in commands:
                if key != 'default':
                    headers = None
                    if commands[key].startswith('/'):
                        obj_exist_key, config = check_if_object_present_absent(server, user, password, command=None, endpoint=commands[key], failed_cmd_out=failed_cmd_out, headers=headers)
                    else:
                        obj_exist_key, config = check_if_object_present_absent(server, user, password, command=commands[key], endpoint=None, failed_cmd_out=failed_cmd_out, headers=headers)   
                    
                    obj_config[key] = config                    

            modify, config_to_modify = check_if_modify_required(arg_dict, obj_key, obj_config, mod_keys=modify_keys, command=None, endpoint=None, diff_config_command_keys=diff_config_command_keys)
        
            if len(modify) > 0:
                commands, payload = build_commands(modify, action, arg_dict, config_to_modify, obj_key, cmd_templates)
                if len(commands) > 0:
                  cmd_combined_out = []
                  for key, command in commands.items():
                    if len(payload) > 0:
                      endpoint = command
                      if key =='del':
                        request_type='delete'
                    
                    else:
                      if key =='del':
                        endpoint = command
                        command = None
                        request_type='delete'
                      else:
                        payload = None
                        endpoint = None
                        request_type = None
                    status, output = change_object(server, user, password, command=command, endpoint=endpoint, request_type=request_type, payload=payload)

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
              cmd_output['changed'] = False
              cmd_output['failed'] = False
        else:
          if arg_dict['state'] == 'present':
            modify = ['create']
            config_to_modify = {}
            keys_to_remove = ['state', 'port']
            if obj_key is None:
                obj_key = []
            for key, value in arg_dict.items():
                if key not in keys_to_remove:
                    if key not in obj_key:
                        if 'create' not in config_to_modify:
                            config_to_modify['create'] = {}            
                        config_to_modify['create'][key] = value
                    else:
                        if 'mod' not in config_to_modify:
                            config_to_modify['mod'] = {}    
                        if key not in config_to_modify['mod']:
                            config_to_modify['mod'][key] = {}
                        for k, v in arg_dict[key].items():
                            config_to_modify['mod'][key][k]= v
        
            commands, payload = build_commands(modify, action, arg_dict, config_to_modify, obj_key, cmd_templates)
            if len(commands) > 0:
              cmd_combined_out = []
              for key, command in commands.items():
                if len(payload) > 0:
                  endpoint = command
                  if 'del' in key:
                    request_type='delete'
                else:
                  payload = None
                  endpoint = None
                  request_type = None
                status, output = change_object(server, user, password, command=command, endpoint=endpoint, request_type=request_type, payload=payload)
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
        

  module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=cmd_output['changed'])


if __name__ == '__main__':
  main()