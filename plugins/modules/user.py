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
module: user
short_description: This module enables you to manage users
version_added: "1.0.0"
description: This module enables you to add, delete users and set password aging and strength options.
  
options:
state:
  type: str
  choices:
  - present
  - absent
  required: true
  description: Use one of the option to run the playbook
name:
  type: str
  required: false
  description: Type the user Name
role:
  type: str
  choices:
  - admin
  - limited-admin
  - user
  - backup-operator
  - none
  required: false
  description: The type of user permissions allowed.
user_password:
  type: str
  required: false
  description: User Password
new_password:
  type: str
  required: false
  description: New User Password. Use when you want to change the password.
destroy:
  type: str
  required: false
  description: Use yes/true for deletion of user. In absense of this key, user will be disabled.
aging:
  type: dict
  description: User password aging
  options:
    all:
      type: bool
      required: false
      description: Use this option only to reset all the password aging options.
    min-days-between-change:
      type: int
      required: false
      description: Minimum number of days allowed before the password can be changed again.
    max-days-between-change:
      type: int
      required: false
      description: Maximum number of days before password expires.
    warn-days-before-expire:
      type: int
      required: false
      description: Number of days of warning before a password expires.
    disable-days-after-expire:
      type: int
      required: false
      description: Account is disabled if inactive for the specified number of days past expiration.
strength:
  type: dict
  description: User Password Strength 
  options:
    all:
      type: bool
      required: false
      description: Use this option only to reset all password strength options
    min-length:
      type: int
      required: false
      description: Ser minimum number of characters in the password. Default 6.
    max-three-repeat:
      type: str
      choices:
      - enabled
      - disabled
      required: false
      description: Enable the requirement for a maximum of three repeated characters. The default setting is disabled.
    passwords-remembered:
      type: int
      required: false
      description: Enable the requirement for a number of previoius passwords remembered
    min-positions-changed:
      type: int
      required: false
      description: MIn Positions changed
    dictionary-match:
      type: str
      choices:
      - enabled
      - disabled
      required: false
      description: Enable the requirement to check for dictionary words
author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
    - name: Add a new user
      dellemc.datadomain.user:
        state: present
        name: 'boostuser02'
        user_password: 'Password@123'
        role: 'none'
				
    - name: Change the password for a user
      dellemc.datadomain.user:
        state: present
        name: 'boostuser02'
        user_password: 'Password@123'
        new_password: 'Password123@'
				
    - name: Change the role of a user
      dellemc.datadomain.user:
        state: present
        name: 'boostuser02'
        role: backup-operator
				
    - name: Disable the user's account
      dellemc.datadomain.user:
        state: absent
        name: 'boostuser02'
				
    - name: Disable the user's account
      dellemc.datadomain.user:
        state: present
        name: 'boostuser02'
				
    - name: Set the password aging policy for a user
      dellemc.datadomain.user:
        state: present
        name: boostuser02
        aging: 
          min-days-between-change: 10
          max-days-between-change: 100
          warn-days-before-expire: 3
          disable-days-after-expire: 10

    - name: Set the password aging policy
      dellemc.datadomain.user:
        state: present
        aging: 
          min-days-between-change: 10
          max-days-between-change: 100
          warn-days-before-expire: 3
          disable-days-after-expire: 10


    - name: Reset the default password aging policy but not all
      dellemc.datadomain.user:
        state: absent
        aging: 
          min-days-between-change: 0
          max-days-between-change: 0

    - name: Reset the default password aging policy for all options
      dellemc.datadomain.user:
        state: absent
        aging: 
          all: yes


    - name: Reset the default password aging policy but not all for a user
      dellemc.datadomain.user:
        state: absent
				name: boostuser02
        aging: 
          min-days-between-change: 0
          max-days-between-change: 0

    - name: Reset the default password aging policy for all options for a user
      dellemc.datadomain.user:
        state: absent
				name: boostuser02
        aging: 
          all: yes

    - name: Reset the one or more options to default password strength policy 
      dellemc.datadomain.user:
        state: absent
        strength: 
          min-length: 0
          max-three-repeat: enabled
	
    - name: Reset the one or more options to default password strength policy 
      dellemc.datadomain.user:
        state: absent
        strength: 
					all: yes
					
    - name: Set the password strength policy
      dellemc.datadomain.user:
        state: present
        strength: 
          min-length: 10
          max-three-repeat: enabled
          passwords-remembered: 3
          min-positions-changed: 1
          dictionary-match: enabled


    - name: Remove a user
      dellemc.datadomain.user:
        state: absent
        name: boostuser02
				destroy: yes
'''


def tab_to_json(output, header=None, rename_keys=None):
    final_data = []
    if rename_keys is None:
        rename_keys = {}
    if "--" in str(output) and "Option" not in str(output) and '- share' not in str(output):
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
                        key, value = o.split(":", 1)
                        key = key.strip().lower().replace(' ', '_')
                        if key in rename_keys:
                            key = rename_keys[key]
                        if len(value.strip()) > 0:

                            data[key] = value.strip()
                        else:
                            data[key] = []
                    else:
                        if len(o) > 0 and '*' not in o:
                            try:
                                key, value = re.split('\s\s+', o.strip())
                                key = key.lower().replace(' ', '_')
                                if key in rename_keys:
                                    key = rename_keys[key]
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


def users():
    condition = dict(
        aging=dict(query=dict(), req_key=['aging'], opt_key=[], will_change=True, header=None),
        strength=dict(query=dict(), req_key=['strength'], opt_key=[], will_change=True, header=None),
        users_service=dict(query=dict(), req_key=[], opt_key=[], will_change=True, header=None)
    )

    cmd_templates = dict(users_service={
        'show':'["/api/v2/dd-systems/0/users/$name"]',
        'add':'["/api/v2/dd-systems/0/users"]',
        'del':'["/rest/v1.0/dd-systems/0/users/$name"]',
        'enable': '["user enable $name"]',
        'disable':'["user disable $name"]',
        'modify': '["/rest/v1.0/dd-systems/0/users/$name"]',
        'change': '["user change role $name $role"]'
    },
    aging={
        'show':'["user password aging option show"]',
        'ushow':'["user password aging show $name"]',
        'set':'["user password aging option set"]',
        'reset':'["user password aging option reset"]',
        'uset':'["user password aging set $name"]',
        'ureset':'["user password aging reset $name"]',
    },
        strength={
        'show':'["user password strength show"]',
        'set':'["user password strength set"]',
        'reset':'["user password strength reset"]'
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
    # if obj_key is None:
    #     obj_key = []

    narg_dict = copy.deepcopy(arg_dict)
    keys_to_remove = ['state', 'port']
    keys_in_dict = list(narg_dict.keys())
    for key in keys_in_dict:
        if key in keys_to_remove:
            del narg_dict[key]
    keys_required_for_payload = {'add': ['name', 'role', 'user_password', 'min_days_between_change', 'max_days_between_change', 'warn_days_before_expire', 'disable_days_after_expire', 'disable_date'], 
                                 'modify': ['user_password', 'new_password'], 'del': []
                                }
    for mod in modify:
        command_to_run = ''
        cmd = cmd_templates[action][mod]
        # if mod == 'show':
        command_to_run = ''
        command_template = Template(cmd)
        command = eval(command_template.substitute(**narg_dict))
        mod_to_check = ['ushow', 'show', 'enable', 'disable']
        if mod not in mod_to_check:
            if command[0].startswith('/'):
                for key in keys_required_for_payload[mod]:
                    if 'days' not in key:
                        if key in narg_dict:
                            if mod == 'modify' and key == 'user_password':
                                a_key = 'current_password'
                            elif mod == 'add' and key == 'user_password':
                                a_key = 'password'
                            else:
                                a_key = key
                            payload[a_key] = narg_dict[key]
                    else:
                        if 'aging' in narg_dict:
                            a_key = key.replace('_', '-')
                            if a_key in narg_dict['aging']:
                                payload[key] = narg_dict['aging'][a_key]

            else:
                if obj_key is not None:
                    if mod == 'reset' or mod == 'ureset':
                        if 'all' in list(narg_dict[obj_key].keys()):
                            if narg_dict[obj_key]['all']:
                                command.append('all')
                            else:
                                for key, value in narg_dict[obj_key].items():
                                    command.append(key)
                        else:
                            for key, value in narg_dict[obj_key].items():
                                    command.append(key)
                    else:
                        command.append(key)
                        command.append(value)
        for arg in command:
            command_to_run = command_to_run + " " + str(arg)
                    
        if command_to_run not in commands:
            command_to_run = command_to_run.replace('[', '').replace("'", '').replace(']', '').strip()
            commands[mod] = command_to_run
    payload = json.dumps(payload)
    return commands, payload      


def check_if_object_present_absent(server, user, password, obj_key=None, command=None, endpoint=None, failed_cmd_out=None, headers=None, rename_keys=None):
    port = 22
    if command is not None:
        cmd_output = dd_connect.dd_ssh(server, user, port, command, private_key=None, password=password, header=headers)
        jsonout = tab_to_json(cmd_output['output'], header=headers, rename_keys=rename_keys)
        status_code = True
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
        if arg_dict['state'] == 'present':
            if 'new_password' in arg_dict and 'role' not in arg_dict:
                if 'modify' not in modify:
                    modify.append('modify')
            elif 'role' in arg_dict and 'new_password' not in arg_dict and 'user_password' not in arg_dict:
                if obj_config['role'] == arg_dict['role']:
                    pass
                else:
                    if 'change' not in modify:
                        modify.append('change')
            else:
                if obj_config['age']['acct_status'] > 1:
                    if 'enable' not in modify:
                        modify.append('enable') 
        else:
            if 'destroy' in arg_dict:
                if arg_dict['destroy']:
                    if 'del' not in modify:
                        modify.append('del')
            else:
                if obj_config['age']['acct_status'] == 1:
                    if 'disable' not in modify:
                        modify.append('disable') 
    else:
        if arg_dict['state'] == 'present':       
            if 'aging' in arg_dict:
                if 'name' in arg_dict:
                    for key, value in arg_dict['aging'].items():
                        if obj_config[0][key] == 'never':
                            obj_config[0][key] = 0
                        
                        if int(value) == int(obj_config[0][key]):
                            pass
                        else:
                            if 'uset' not in modify:
                                modify.append('uset')
                            if 'uset' not in config_to_modify:
                                config_to_modify['uset'] = {}
                            config_to_modify['uset'][key] = int(value)
                else:
                    for key, value in arg_dict['aging'].items():
                        if obj_config[0][key] == 'never':
                            obj_config[0][key] = 0
                        
                        if int(value) == int(obj_config[0][key]):
                            pass
                        else:
                            if 'set' not in modify:
                                modify.append('set')
                            if 'set' not in config_to_modify:
                                config_to_modify['set'] = {}
                            config_to_modify['set'][key] = int(value)
            else:
                for key, value in arg_dict[obj_key].items():
                    
                    try:
                        value = int(value)
                    except ValueError:
                        value = value
                    else:
                        value = int(value)
                        obj_config[0][key] = int(obj_config[0][key])
                    if value == obj_config[0][key]:
                        pass
                    else:
                        if 'set' not in modify:
                            modify.append('set')
                        if 'set' not in config_to_modify:
                            config_to_modify['set'] = {}
                        config_to_modify['set'][key] = value

        else:
            if 'aging' in arg_dict:
                if 'name' in arg_dict:
                    for key, value in arg_dict['aging'].items():
                        
                        if 'ureset' not in modify:
                            modify.append('ureset')
                        if 'ureset' not in config_to_modify:
                            config_to_modify['ureset'] = {}
                        config_to_modify['ureset'][key] = value
                else:
                    for key, value in arg_dict['aging'].items():
                        if 'reset' not in modify:
                            modify.append('reset')
                        if 'reset' not in config_to_modify:
                            config_to_modify['reset'] = {}
                        config_to_modify['reset'][key] = value
            else:
                for key, value in arg_dict[obj_key].items():
                    if 'reset' not in modify:
                        modify.append('reset')
                    if 'reset' not in config_to_modify:
                        config_to_modify['reset'] = {}
                    config_to_modify['reset'][key] = value

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
    fields = {'state': {'type': 'str', 'choices': ['present', 'absent'], 'required': True},
              'name': {'type': 'str', 'required': False},
              'role': {'type': 'str',  'choices': ['admin', 'limited-admin', 'user', 'backup-operator', 'none'], 'required': False},
              'user_password': {'type': 'str', 'required': False},
              'new_password': {'type': 'str', 'required': False},
              'destroy': {'type': 'bool', 'required': False},
            'aging': {'type': 'dict', 'options':  {'all': {'type': 'bool', 'required': False}, 
            'min-days-between-change': {'type': 'int', 'required': False},
                        'max-days-between-change': {'type': 'int', 'required': False}, 'warn-days-before-expire': {'type': 'int', 'required': False},
                        'disable-days-after-expire': {'type': 'int', 'required': False}}
                        },
        'strength': {'type': 'dict', 'options':  {'all': {'type': 'bool', 'required': False},
                    'min-length': {'type': 'int', 'required': False},
                    'max-three-repeat': {'type': 'str',  'choices': ['enabled', 'disabled'], 'required': False}, 
                    'passwords-remembered': {'type': 'int',  'required': False}, 
                    'min-positions-changed': {'type': 'int', 'required': False},
                    'dictionary-match': {'type': 'str', 'choices': ['enabled', 'disabled'], 'required': False}}
                    },
        'host': {'type': 'str', 'required': True},
        'port': {'type': 'int', 'default': 22},
        'username': {'type': 'str', 'required': True},
        'private_key': {'type': 'str', 'no_log': True},
        'password': {'type': 'str', 'no_log': True},
    }
    module = AnsibleModule(argument_spec=fields, mutually_exclusive=[('private_key', 'password'), ('aging', 'strength')],
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
    conditions, cmd_templates = users()
    failed_cmd_out = ['Invalid']
    cmd_output = {}
    obj_keys = ['aging', 'strength']
    obj_key = get_obj_key(arg_dict, obj_keys)
    headers = []
    action = condition_check(conditions, command_build_dict=arg_dict)
    headers = None
    rename_keys = {'minimum_days_between_password_change': 'min-days-between-change', 'maximum_days_between_password_change': 'max-days-between-change', 'warning_days_between_password_change': 'warn-days-before-expire', 'disable_days_after_expire': 'disable-days-after-expire',
    'Minimum password length': 'min-length', 'Minimum character classes': 'min-character-classes', 'At least one lowercase character': 'one-lowercase-char', 'At least one uppercase character': 'one-uppercase-char', 'At least one digit': 'one-digit', 'At least one special character': 'one-special-character', 'At most three consecutive repeated characters': 'max-three-repeat', 'Passwords remembered': 'passwords-remembered', 'Minimum positions changed': 'min-positions-changed', 'Check password against common words': 'dictionary-match'}

    if obj_key == 'aging':
        if "name" in arg_dict:
            modify = ['ushow']
            headers = ['name', 'last_pass_changed', 'min-days-between-change', 'max-days-between-change', 'warn-days-before-expire', 'disable-days-after-expire', 'status']
        else:
            modify = ['show']
    else:
        modify = ['show']

    if len(action) > 0:
        commands, payload = build_commands(modify, action, arg_dict, obj_key, cmd_templates)
        if len(commands) > 0:
            for command in commands:
                if commands[command].startswith('/'):
                    obj_exist, obj_config = check_if_object_present_absent(server, user, password, obj_key=None, command=None, endpoint=commands[command], failed_cmd_out=None, headers=None)
                else:
                    obj_exist, obj_config = check_if_object_present_absent(server, user, password, obj_key=obj_key, command=commands[command], endpoint=None, failed_cmd_out=failed_cmd_out, headers=headers, rename_keys=rename_keys)
                if obj_exist:
                    modify, config_to_modify = check_if_modify_required(arg_dict, obj_key, obj_config)
                    if len(modify) > 0:
                        commands, payload = build_commands(modify, action, arg_dict, obj_key, cmd_templates)
                        if len(commands) > 0:
                            for key in commands:
                                command = commands[key]
                                if command.startswith('/'):
                                    if key == 'del':
                                        request_type = 'delete'
                                    elif key == 'modify':
                                        request_type = 'put'
                                    else:
                                        request_type = None
                                    status, output = change_object(server, user, password, command=None, endpoint=command, request_type=request_type, payload=payload)
                                else:
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
                        cmd_output['output'] = obj_config
                        cmd_output['changed'] = False
                        cmd_output['failed'] = False    
                else:
                    if arg_dict['state'] == 'present':
                        req_keys = ['name', 'role', 'user_password']
                        req_keys_check = []
                        keys_in_arg_dict = list(arg_dict.keys())
                        for key in req_keys:
                            if key in keys_in_arg_dict:
                                req_keys_check.append(True)
                            else:
                                req_keys_check.append(False)
                        if all(req_keys_check):
                            action = 'users_service'
                            modify = ['add']
                            commands, payload = build_commands(modify, action, arg_dict, obj_key, cmd_templates)
                            if len(commands) > 0:
                                for key in commands:
                                    command = commands[key]
                                    if command.startswith('/'):
                                        if key == 'add':
                                            request_type = 'post'
                                        else:
                                            request_type = None
                                        status, output = change_object(server, user, password, command=None, endpoint=command, request_type=request_type, payload=payload)
                                    else:
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
                            cmd_output['output'] = 'To add new user, at minimum, provide name, user_password, role parameters'
                            cmd_output['failed'] = True
                            cmd_output['changed'] = False
                    else:
                        cmd_output['output'] = 'User does not exists'
                        cmd_output['failed'] = False
                        cmd_output['changed'] = False
    else:
        cmd_output['output'] = 'Please check the input parameters and rerun the playbook.'
        cmd_output['failed'] = False
        cmd_output['changed'] = False
    
    module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=cmd_output['changed'])


if __name__ == '__main__':
    main()