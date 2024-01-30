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
  timeserver:
    type: list
    required: false
    description: 'Type the list of IPs or FQDN if timeservers'
  reset:
    type: bool
    description: 'If true with absent state, it will reset the configuration to default values.'
author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
        
  - name: Enable the NTP local server
    dellemc.datadomain.ntp:
        state: present


  - name: Disable the NTP local server
    dellemc.datadomain.ntp:
        state: absent

  - name: Add one or more remote time servers
    dellemc.datadomain.ntp:
        state: present
        timeserver:
            - 10.0.0.1
            - 10.0.0.2

  - name: Delete one or more remote time servers
    dellemc.datadomain.ntp:
        state: absent
        timeserver:
            - 10.0.0.1

  - name: Disable the NTP local server
    dellemc.datadomain.ntp:
        state: absent
	    reset: yes

  - name: Add one or more remote time servers
    dellemc.datadomain.ntp:
        state: absent
        timeserver:
        reset: yes

'''

def check_if_object_present_absent(server, user, password, command=None, endpoint=None, failed_cmd_out=None, headers=None):
    port = 22
    if command is not None:
        cmd_output = dd_connect.dd_ssh(server, user, port, command, private_key=None, password=password, header=None)
        jsonout = dd_connect.tab_to_json(output=cmd_output['output'], header=headers)
 
        if not cmd_output['failed']:
            if not failed_cmd_out in str(cmd_output['output']):
                return [True, jsonout]
            else:
                return [False, jsonout]
        else:
            return [False, jsonout]


def check_if_modify_required(arg_dict, obj_key, obj_config, mod_keys=None, command=None, endpoint=None):
    modify = []
    if obj_key is not None:
        obj_config_tobe = copy.deepcopy(arg_dict[obj_key])
    else:
        obj_config_tobe = copy.deepcopy(arg_dict)
    keys_to_remove = ['state', 'port', 'name']
    for key in keys_to_remove:
        if key in obj_config_tobe:
            try:
                del obj_config_tobe[key]
            except KeyError:
                pass
    
    if arg_dict['state'] == 'present':
        if len(obj_config_tobe) > 0:
            for key, value in obj_config_tobe.items():
                
                if isinstance(value, list):
                    value.sort()
                    
                    if isinstance(obj_config, list):
                        obj_config_list = []
                        for obj in obj_config:
                            if key in obj:
                                obj_config_list.append(obj[key])
                                
                    else:
                        obj_config_list = obj_config[key]
                    for v in value:
                        if v in obj_config_list:
                            pass
                        else:
                            
                            if 'add' not in modify:
                                modify.append('add')
                    
                else:
                    if obj_key is not None:
                        if value == obj_config[key]:
                            pass
                        else:
                            if 'mod' not in modify:
                                modify.append('mod')
                    else:
                    
                        if 'add' not in modify:
                            modify.append('add')   
        else:
            if 'enabled' in str(obj_config).lower():
                pass
            else:
                if 'add' not in modify:
                    modify.append('add')
    else:
        if obj_key is not None:
            if len(mod_keys[obj_key])> 0:
                for key in mod_keys[obj_key]:
                    if key in obj_config_tobe:
                        del obj_config_tobe[key]
        if 'reset' in arg_dict:
            if arg_dict['reset']:
                if 'reset' not in modify:
                    modify.append('reset')
        else:
            if len(obj_config_tobe) > 0:
                for key, value in obj_config_tobe.items():
                    if isinstance(value, list):
                        value.sort()
                        if isinstance(obj_config, list):
                            obj_config_list = []
                            for obj in obj_config:
                                if key in obj:
                                    obj_config_list.append(obj[key])
                        else:
                            obj_config_list = obj_config[key]
                        obj_config_list.sort()
                        for v in value:
                            if v in  obj_config_list:
                                if 'del' not in modify:
                                    modify.append('del')
                            else:
                                pass
                    else:
                        if obj_key is not None:
                            if value == obj_config[key]:
                                if 'del' not in modify:
                                    modify.append('del')
                            else:
                                pass
                        else:
                            if 'del' not in modify:
                                modify.append('del')   
            else:
                if 'disabled' in str(obj_config).lower():
                    pass
                else:
                    if 'del' not in modify:
                        modify.append('del')
    return modify


def get_obj_key(arg_dict, obj_keys):
    for obj in obj_keys:
        if obj in arg_dict:
            return obj
            break


def change_object(server, user, password, command=None, endpoint=None):
    port = 22
    if command is not None:
        cmd_output = dd_connect.dd_ssh(server, user, port, command, private_key=None, password=password, header=None)
        jsonout = dd_connect.tab_to_json(output=cmd_output['output'])
        if not cmd_output['failed']:
            return [True, jsonout]
        else:
            return [False, jsonout]


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


def ntp():
    conditions = dict(

        ntp_timeserver=dict(query=dict(), req_key=['timeserver'], opt_key=[], will_change=True, header=None),
        ntp_service=dict(query=dict(), req_key=[], opt_key=[], will_change=True, header=None),
       
    )

    cmd_templates = dict(ntp_timeserver={'show': '["ntp show config"]',
                                         'add':'["ntp add timeserver $timeserver"]',
                                         'del':'["ntp del timeserver $timeserver"]',
                                         'reset': '["ntp reset timeservers"]'
                                         },
                    ntp_service={'show': '["ntp status "]',
                                            'add': '["ntp enable"]',
                                              'del':   '["ntp disable"]',
						                    'reset': '["ntp reset"]'
                                            }
                    
    )

    return conditions, cmd_templates


def build_commands(modify, action, arg_dict, modify_keys, obj_key, cmd_templates):
    commands = []
    for mod in modify:
        command_to_run = ''
        cmd = cmd_templates[action][mod]
        if len(cmd) > 0:
            command_template = Template(cmd)
            if obj_key is not None:
                command = eval(command_template.substitute(**arg_dict[obj_key]))
                if mod == 'mod':
                    for key, value in arg_dict[obj_key].items():
                        if key in modify_keys[obj_key]:
                            command.append(key)
                            command.append(value)
                elif mod == 'add' or mod == 'del':
                    for key, value in arg_dict[obj_key].items():
                        if key != 'state' and key != 'name':
                            if key not in modify_keys[obj_key]:
                                command.append(key)
                                command.append(value)
                            # if isinstance(value, list):
                            #     for v in value:
                            #         command.append(v)
                elif mod == 'create':
                    for key, value in arg_dict[obj_key].items():
                        if key != 'state' and key != 'name':
                            command.append(key)
                            command.append(value)
                else:
                    command = eval(command_template.substitute(**arg_dict[obj_key]))
            else:
                if action == 'compression_service' and mod == 'add':
                    if arg_dict['initialize']:
                        command = eval(command_template.substitute(**arg_dict))
                        command.append('and-initialize')
                    else:
                        command = eval(command_template.substitute(**arg_dict))
                else:
                    command = eval(command_template.substitute(**arg_dict))
            for arg in command:
                command_to_run = command_to_run + " " + str(arg)
            if command_to_run not in commands:
                command_to_run = command_to_run.replace('[', '').replace("'", '').replace(']', '').strip()

                commands.append(command_to_run)
    return commands      


def obj_config_remove_str(str_list_to_remove, obj_config):
    for key, value in obj_config.items():
        for string in str_list_to_remove:
            if isinstance(value, list):
                for idx, v in enumerate(value):
                    if string in v:
                        obj_config[key][idx] = v.replace(string, '').strip()
            else:
                obj_config[key] = value.replace(string, '').strip()
    return obj_config


def schedule_frequency(arg_dict, obj_key):
    num_day_dict = {0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat', 7: 'Sun'}
    day_names = []
    frequency = ''
    if obj_key == 'schedule':
        if 'day' in arg_dict['schedule']:
            num_days = arg_dict['schedule']['day'].split(',')
            frequency = 'weekly on '
            for day in num_days:

                if isinstance(eval(day.strip()), int):
                    day_names.append(num_day_dict[eval(day)])
                else:
                    day_names.append(day.strip().capitalise())
            for day in day_names:
                frequency = frequency + day + ', '
            frequency = frequency.rstrip(', ')
        elif 'monthly' in arg_dict['schedule']:
            frequency = 'monthly on day(s) '
            num_days = arg_dict['schedule']['monthly'].split(',')
            for day in num_days:
                frequency = frequency + day + ', '
            frequency = frequency.rstrip(', ')
    return frequency


def modify_arg_dict_for_modify_check(arg_dict, frequency, obj_key):
    formatted_arg_dict = {}
    for key, value in arg_dict.items():
        
        if isinstance(value, dict):
            if obj_key not in formatted_arg_dict:
                formatted_arg_dict[key] = {}
            for k, v in arg_dict[key].items():
                if k == 'day' or k == 'monthly':
                    formatted_arg_dict[key]['frequency'] = frequency
                elif k == 'mtrees':
                    formatted_arg_dict[key]['mtree(s)'] = v
                else:
                    formatted_arg_dict[key][k] = v

        else:
            formatted_arg_dict[key] = value

    return formatted_arg_dict


def main():

    conditions, cmd_templates = ntp()
    fields = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'required': True},
        'timeserver': {'type': 'list', 'required': False},
        'reset': {'type': 'bool', 'required': False},
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
    failed_cmd_out = 'No '
    str_list_to_remove = []
    obj_keys = []
    modify_keys = {}
    obj_key = get_obj_key(arg_dict, obj_keys)
    action = condition_check(conditions, command_build_dict=arg_dict)
    modify = ['show']

    if len(action) > 0:
        if 'timeserver' in arg_dict:
            headers = ['sr', 'timeserver']
        else:
            headers = None
        
        commands = build_commands(modify, action, arg_dict, modify_keys, obj_key, cmd_templates)
        command = commands[0]
        obj_exist, obj_config = check_if_object_present_absent(server, user, password, command=command, endpoint=None, failed_cmd_out=failed_cmd_out, headers=headers)

        if obj_exist:
            modify = check_if_modify_required(arg_dict, obj_key, obj_config=obj_config, mod_keys=modify_keys ,command=None, endpoint=None)
            # cmd_output['output'] = modify
            # cmd_output['changed'] = True
            # cmd_output['failed'] = False
            if len(modify) > 0:
                commands = build_commands(modify, action, arg_dict, modify_keys, obj_key, cmd_templates)

                if len(commands) > 0:
                    for command in commands:
                        status, output = change_object(server, user, password, command=command, endpoint=None)
                        if status:
                            cmd_output['output'] = output
                            cmd_output['changed'] = True
                            cmd_output['failed'] = False
                        else:
                            cmd_output['output'] = output
                            cmd_output['changed'] = False
                            cmd_output['failed'] = True
                            break
                else:
                    cmd_output['output'] = f"Configuration is already in same state as requested. So no Modifications required"
                    cmd_output['failed'] = False
                    cmd_output['changed'] = False
            else:
                cmd_output['output'] = f"Configuration is already in same state as requested. So no Modifications required"
                cmd_output['failed'] = False
                cmd_output['changed'] = False

        else:
            if arg_dict['state'] == 'present':
                if 'disabled' in str(obj_config):
                    modify = ['add']
                    commands_en = build_commands(modify, 'ntp_service', arg_dict, modify_keys, obj_key, cmd_templates)
                    
                else:
                    commands_en = []    

                modify = ['add']
                commands = build_commands(modify, action, arg_dict, modify_keys, obj_key, cmd_templates)
                if len(commands_en) > 0:
                    for cmd in commands_en:
                        commands.insert(0,cmd)
                if len(commands) > 0:
                    for command in commands:
                        status, output = change_object(server, user, password, command=command, endpoint=None)
                        if status:
                            cmd_output['output'] = output
                            cmd_output['changed'] = True
                            cmd_output['failed'] = False
                        else:
                            cmd_output['output'] = output
                            cmd_output['changed'] = False
                            cmd_output['failed'] = True
                            break
            else:
                cmd_output['output'] = 'Configuration Item does not exist. No Action is needed.'
                cmd_output['changed'] = False
                cmd_output['failed'] = False

    else:
        cmd_output['output'] = "As per playbook condition, no action matched. Please re-check documentation and rerun the playbook"
        cmd_output['failed'] = True
        cmd_output['changed'] = False

        module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=cmd_output['changed'])

    module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=cmd_output['changed'])


if __name__ == '__main__':
    main()