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
import copy
from string import Template


DOCUMENTATION = r'''
---
module: cifs
short_description: This module is used to manage the CIFS services on datadomain
version_added: "1.0.0"
description: This module supported below actions on CIFS services
  - cifs enable
  - cifs disable
  - cifs share create
  - cifs share modify
  - cifs share enable
  - cifs share disable
  - cifs share destroy
  
options:
  state:
    type: str
    choices:
    - present, absent
    required: true
    description: 'Choose the option from the choices above'
  share:
    type: str
    description: 'Type the share name'
    options:
        path:
            type: str
            description: 'Type the path of the directory. it should start with /backup or /ddvar'
        max-connections:
            type: str
            description: 'Maximum connections'
        destroy:
            type: bool
            description: 'If combined with absent state, it will delete the share.'
        clients:
            type: list
            description: 'Client IPs who can access the share. Type "*" if you want to allow all hosts (not recommemded)'
        users:
            type: list
            description: 'Type user names who can access the share.'
  
author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
    - name: Enable CIFS
      dellemc.datadomain.cifs:
        state: present
    
    - name: Disable CIFS
      dellemc.datadomain.cifs:
        state: absent

    - name: Create a Share
      dellemc.datadomain.cifs:
        state: present
        share:
          name: backup3
          path: /data/col1/backup
          clients:
              - 10.0.0.3
              - 10.0.0.4

    - name: Modify a Share max_connections
      dellemc.datadomain.cifs:
        state: present
        share:
          name: backup2
          max_connections: 20


    - name: Modify a Share clients or users
      dellemc.datadomain.cifs:
        state: present
        share:
          name: backup2
          clients:
            - 10.0.0.3
            - 10.0.0.4
          users:
            - sysadmin
  
    - name: Delete a clients or users access from share
      dellemc.datadomain.cifs:
        state: absent
        share:
          name: backup2
          clients:
            - 10.0.0.4
          users:
            - sysadmin

    - name: Disable a share
      dellemc.datadomain.cifs:
        state: absent
        share:
          name: backup2

'''


def tab_to_json(output, header=None, rename_keys=None):
    final_data = {}
    list_keys = ['clients', 'users']
    process_data = output.strip().split('\n')
    for line in process_data:
        if 'CIFS is ' in line:
            status = line.split(' ')[-1]
            if status == 'enabled.':
                final_data['status'] = True
            else:
                final_data['status'] = False
        else:
            if len(line.strip()) > 0:
                if 'share' not in final_data:
                    final_data['share'] = {}
                if '--' in line:
                    
                    share = line.strip('-').strip().split(' ')[1]
                    final_data['share']['name'] = share
                else:
                    if 'displayed' not in line and 'Shares information for' not in line and 'does not exist' not in line:
                        key, value = line.strip().split(': ')
                        
                        if key in rename_keys:
                            key = rename_keys[key]
                        else:
                            key = key
                        if key in list_keys:
                            if key not in final_data['share']:
                                final_data['share'][key] = []
                        else:
                            if key not in final_data['share']:
                                final_data['share'][key] = ''
                        if isinstance(final_data['share'][key], list):
                            final_data['share'][key].append(value)
                        else:
                            final_data['share'][key] = value
    return final_data


def cifs():
  conditions = dict(
    share=dict(query=dict(), req_key=['share'], opt_key=[], will_change=True, header=None),
    cifs_service=dict(query=dict(), req_key=[], opt_key=[], will_change=True, header=None))
  command_template = dict(share={
        'show':'["cifs share show $name"]',
        'create':'["/rest/v1.0/dd-systems/0/protocols/cifs/shares"]',
        'mod':'["/rest/v1.0/dd-systems/0/protocols/cifs/shares/$name"]',
        'del':'["/rest/v1.0/dd-systems/0/protocols/cifs/shares/$name"]',
        },
        cifs_service={
            'show':'["cifs status"]',
            'enable':'["cifs enable"]',
            'disable':'["cifs disable"]'
        }
        )
  headers = dict()
  rename_keys = dict(share={'maxconn': 'max_connections'})
  return conditions, command_template, headers, rename_keys


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


def get_obj_key(arg_dict, obj_keys):
    for obj in obj_keys:
        if obj in arg_dict:
            return obj
            break


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
        
        command_to_run = ''
        
        command_template = Template(cmd)
        command = eval(command_template.substitute(**narg_dict))
        if mod in config_to_modify:
            for key, value in config_to_modify[mod].items():
                payload[key] = value
                
        for arg in command:
            command_to_run = command_to_run + " " + str(arg)
        if command_to_run not in commands:
            command_to_run = command_to_run.replace('[', '').replace("'", '').replace(']', '').strip()
            commands[mod] = command_to_run

    payload = json.dumps(payload)
    return commands, payload


def check_if_object_present_absent(server, user, password, obj_key=None, command=None, endpoint=None, failed_cmd_out=None, headers=None, rename_keys=None, search_obj=None):
    port = 22
    if command is not None:
        hostname_command = 'net show hostname'
        cmd_output = dd_connect.dd_ssh(server, user, port, command=hostname_command, private_key=None, password=password, header=headers)
        hostname = cmd_output['output'].strip().split(': ')[1].split('.')[0]
        cmd_output = dd_connect.dd_ssh(server, user, port, command, private_key=None, password=password, header=headers)
        jsonout = tab_to_json(output=cmd_output['output'], header=None, rename_keys=rename_keys)
        if obj_key is not None:
            jsonout['share']['hostname'] = hostname
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
    if obj_key is None:
        temp_req_config = copy.deepcopy(arg_dict)
    else:
        temp_req_config = copy.deepcopy(arg_dict[obj_key])
        obj_config = obj_config[obj_key]
    for key in arg_dict:
        if key in keys_to_remove:
            if key in temp_req_config:
                del temp_req_config[key]
    if arg_dict['state'] == 'present':
        if obj_key is not None:
            if obj_config['enabled'] != 'yes':
                if 'mod' not in modify:
                    modify.append('mod')
                if 'mod' in config_to_modify:
                    config_to_modify['mod'] = {}
                if 'disable' not in config_to_modify:
                    config_to_modify['mod']['disable'] = False   
            for prop in temp_req_config:
                if prop == 'users':
                    for idx, u in enumerate(temp_req_config[prop]):
                        if '\\' not in u:
                            hostname = obj_config['hostname']
                            temp_req_config[prop][idx] = f'{hostname}\{u}'
                if isinstance(temp_req_config[prop], list):
                    if prop in obj_config:
                        temp_req_config[prop].sort()
                        obj_config[prop].sort()
                        if temp_req_config[prop] == obj_config[prop]:
                            pass
                        else:
                            if '*' in obj_config[prop]:
                                if 'mod' not in config_to_modify:
                                    config_to_modify['mod'] = {}
                                if prop not in config_to_modify['mod']:
                                    config_to_modify['mod'][prop] = []
                                config_to_modify['mod'][prop].append({'name': '*', 'delete': True})
                                for obj in temp_req_config[prop]:
                                    if 'mod' not in modify:
                                        modify.append('mod')
                                    if 'mod' not in config_to_modify:
                                        config_to_modify['mod'] = {}
                                    if prop not in config_to_modify['mod']:
                                        config_to_modify['mod'][prop] = []
                                    config_to_modify['mod'][prop].append({'name': obj}) 
                                    
                            else:
                                if obj not in obj_config[prop]:
                                    if 'mod' not in modify:
                                        modify.append('mod')
                                    if 'mod' not in config_to_modify:
                                        config_to_modify['mod'] = {}
                                    if prop not in config_to_modify['mod']:
                                        config_to_modify['mod'][prop] = []
                                    for cl in obj_config[prop]:
                                        if cl not in config_to_modify['mod'][prop]:
                                            config_to_modify['mod'][prop].append({'name': cl})
                                    # config_to_modify['mod'][prop].append(obj)
                                else:
                                    pass
                    else:
                        if 'mod' not in modify:
                            modify.append('mod')
                        if 'mod' not in config_to_modify:
                            config_to_modify['mod'] = {}
                        if prop == 'users':
                            if prop not in config_to_modify['mod']:
                                config_to_modify['mod'][prop] = []
                            for obj in temp_req_config[prop]:
                                config_to_modify['mod'][prop].append({'name': obj})
                        else:
                            config_to_modify['mod'][prop] = temp_req_config[prop]

                else:
                    if prop in obj_config:
                        if str(temp_req_config[prop]) == str(obj_config[prop]):
                            pass
                        else:
                            if 'mod' not in modify:
                                modify.append('mod')
                            if 'mod' not in config_to_modify:
                                config_to_modify['mod'] = {}
                            if prop not in config_to_modify['mod']:
                                config_to_modify['mod'][prop] = ''
                            config_to_modify['mod'][prop] = temp_req_config[prop]
                    else:
                        if 'mod' not in modify:
                            modify.append('mod')
                        if 'mod' not in config_to_modify:
                            config_to_modify['mod'] = {}

                        config_to_modify['mod'][prop] = temp_req_config[prop]
                        
        else:
            if obj_config['status']:
                pass
            else:
                if 'enable' not in modify:
                    modify.append('enable')
    else:
        if obj_key is not None:
            num_keys = len(temp_req_config)

            if 'destroy' in temp_req_config:
                if temp_req_config['destroy']:
                    if 'del' not in modify:
                        modify.append('del')
                else:
                    pass
            else:
                if num_keys == 1 and 'name' in temp_req_config:
                    if obj_config['enabled'] == 'yes':
                        if 'destroy' in temp_req_config:
                            if temp_req_config['destroy']:
                                if 'del' not in modify:
                                    modify.append('del')
                            else:
                                if 'mod' not in modify:
                                    modify.append('mod')
                                if 'mod' not in config_to_modify:
                                    config_to_modify['mod'] = {}
                                if 'disable' not in config_to_modify['mod']:
                                    config_to_modify['mod']['disable'] = True
                        else:
                            if 'mod' not in modify:
                                modify.append('mod')
                            if 'mod' not in config_to_modify:
                                config_to_modify['mod'] = {}
                            if 'disable' not in config_to_modify['mod']:
                                config_to_modify['mod']['disable'] = True
                else:
                    for prop in temp_req_config:
                        if prop == 'users':
                            for idx, u in enumerate(temp_req_config[prop]):
                                if '\\' not in u:
                                    hostname = obj_config['hostname']
                                    temp_req_config[prop][idx] = f'{hostname}\{u}'
                        if isinstance(temp_req_config[prop], list):
                            if prop in obj_config:
                                temp_req_config[prop].sort()
                                obj_config[prop].sort()
                                
                                for obj in temp_req_config[prop]:
                                    if '*' in obj_config[prop]:
                                        pass
                                    else:
                                        if obj not in obj_config[prop]:
                                            pass
                                        else:
                                                                                        
                                            if 'mod' not in modify:
                                                modify.append('mod')
                                            if 'mod' not in config_to_modify:
                                                config_to_modify['mod'] = {}
                                            # if 'delete' not in config_to_modify['mod']:
                                            #     config_to_modify['mod']['delete'] = True
                                            if prop not in config_to_modify['mod']:
                                                config_to_modify['mod'][prop] = []
                                            if obj in obj_config[prop]:
                                                config_to_modify['mod'][prop].append({'name': obj, 'delete': True})

                        else:
                            pass
        else:
            if obj_config['status']:
                if 'disable' not in modify:
                    modify.append('disable')
            else:
                pass

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
        
        'share': {'type': 'dict', 'required': False, 'option':{
            'name': {'type': 'str', 'required': False},
            'path': {'type': 'str', 'required': False},
            'max_connections': {'type': 'str'},
            'clients': {'type': 'list'},
            'users': {'type': 'list'},
            'comment': {'type': 'text'},
            'destroy': {'type': 'bool'},
        }},
        'host': {'type': 'str', 'required': True},
        'port': {'type': 'int', 'default': 22},
        'username': {'type': 'str', 'required': True},
        'password': {'type': 'str', 'no_log': True},
      }
    module = AnsibleModule(argument_spec=fields, mutually_exclusive=[('private_key', 'password'), ('aging', 'strength')],
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
    conditions, cmd_templates, headers, rename_keys = cifs()
    obj_keys = ['share']
    obj_key = get_obj_key(arg_dict, obj_keys)
    if obj_key is not None:
        rename_keys = rename_keys[obj_key]
    else:
        rename_keys = None
    failed_cmd_out = ['does not exist']
    action = condition_check(conditions, command_build_dict=arg_dict)
    modify = ['show']
    if len(action) > 0:
        commands, payload = build_commands(modify, action, arg_dict, obj_key, cmd_templates, config_to_modify={})
        if len(commands) > 0:
            if commands[modify[0]].startswith('/'):
                obj_exists, obj_config = check_if_object_present_absent(server, user, password, obj_key=obj_key, command=None, endpoint=commands[modify[0]], failed_cmd_out=failed_cmd_out, headers=None, rename_keys=rename_keys, search_obj=None)    
            else:
                obj_exists, obj_config = check_if_object_present_absent(server, user, password, obj_key=obj_key, command=commands[modify[0]], endpoint=None, failed_cmd_out=failed_cmd_out, headers=None, rename_keys=rename_keys, search_obj=None)

            if obj_exists:
                modify, config_to_modify = check_if_modify_required(arg_dict, obj_key, obj_config)
                if len(modify) > 0:
                    commands, payload = build_commands(modify, action, arg_dict, obj_key, cmd_templates, config_to_modify=config_to_modify)
                    # cmd_output['output'] = (commands, payload)
                    # cmd_output['failed'] = False
                    # cmd_output['changed'] = False
                    if len(commands) > 0:
                        cmd_combined_out = []
                        request_types = {'mod': 'put', 'del': 'delete', 'create': 'post'}
                        for key, command in commands.items():
                            if command.startswith('/'):
                                endpoint = command
                                request_type = request_types[key]
                                command = None
                            else:
                                payload = None
                                endpoint = None
                                request_type = None
                            status, output = change_object(server, user, password, command=command, endpoint=endpoint, request_type=request_type, payload=payload)
                            status = 'SUCCESS' if status else 'FAILED'
                            cmd_combined_out.append({'status': status, 'output': output})
                            if status != 'SUCCESS':
                                cmd_output['failed'] = True
                                cmd_output['output'] = cmd_combined_out
                                cmd_output['changed'] = True
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
                    req_keys = ['name', 'path']
                    req_keys_check = []
                    keys_in_arg_dict = list(arg_dict[obj_key].keys())
                    for key in req_keys:
                        if key in keys_in_arg_dict:
                            req_keys_check.append(True)
                        else:
                            req_keys_check.append(False)
                    if all(req_keys_check):
                        config_to_modify = {}
                        action = 'share'
                        modify = ['create']
                        if 'create' not in config_to_modify:
                            config_to_modify['create'] = {}
                        config_to_modify['create'] = arg_dict['share']
                        commands, payload = build_commands(modify, action, arg_dict, obj_key, cmd_templates, config_to_modify)
                        if len(commands) > 0:
                            cmd_combined_out = []
                            request_types = {'mod': 'put', 'del': 'delete', 'create': 'post'}
                            for key, command in commands.items():
                                if command.startswith('/'):
                                    endpoint = command
                                    request_type = request_types[key]
                                    command = None
                                else:
                                    payload = None
                                    endpoint = None
                                    request_type = None
                                status, output = change_object(server, user, password, command=command, endpoint=endpoint, request_type=request_type, payload=payload)
                                status = 'SUCCESS' if status else 'FAILED'
                                cmd_combined_out.append({'status': status, 'output': output})
                                if status != 'SUCCESS':
                                    cmd_output['failed'] = True
                                    cmd_output['output'] = cmd_combined_out
                                    cmd_output['changed'] = True
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
                        cmd_output['output'] = 'Not all required arguments were passed. Please check the playbook and resubmit the action.'
                        cmd_output['failed'] = False
                        cmd_output['changed'] = False
                        
    else: 
        cmd_output['output'] = 'Please check the input parameters and rerun the playbook.'
        cmd_output['failed'] = False
        cmd_output['changed'] = False

    module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=cmd_output['changed'])


if __name__ == '__main__':
    main()