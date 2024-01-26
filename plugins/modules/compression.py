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
import re
import copy
from string import Template

DOCUMENTATION = r'''
---
module: config
short_description: This module is used to manage the configuration using Physical Compression reporting using compression command.
version_added: "1.0.0"
description: This module is used to manage the configuration using Physical Compression reporting using compression command.

  
options:
  state:
    type: str
    choices:
        - present, absent
    required: true
    description: 'Choose the option from the choices above'
  pathset:
    type: dict
    description: 'Use this option to create, modify or destroy pathset'
    option:
      name:
        type: str
        description: 'Type the name of the pathset'
      paths:
        type: list
        description: 'Type the mtree names in list format. make sure path exists'  
      measurement-retention:
        type: str
        description: 'Type the number of days you want to retain the measurement. 180 days is the default value.'  
  schedule:
    type: dict
    description: 'Use this option to create, modify or destroy schedule'
    option:
      name:
        type: str
        description: 'Type the name of the schedule'
      pathsets:
        type: list
        description: 'Type the pathset names in list format'
      tenants:
        type: list
        description: 'Type the tenant names in list format'
      tenants-units:
        type: list
        description: 'Type the tenant-unit names in list format'
      mtrees:
        type: list
        description: 'Type the mtree names in list format'
      priority:
        type: str
        description: 'select the priority to start the scheduled measurement task'
        choices:
            - normal
            - urgent
      time:
        type: str
        description: 'Type the schedule start time in 24 hour format e.g. 13:00'

      day:
        type: list
        description: 'With the keyword day, specify days as the days of the week using either lowercase, three letter abbreviations for the days of the week: mon, tue, wed, thu, fri, sat, sun, or as integers: 0 = Sunday, 1 = Monday, 2 = Tuesday, 3 = Wednesday, 4 = Thursday, 5 = Friday, 6 = Saturday'
        
      monthly:
        type: str
        description: Specify the days of the month using integers (1-31) and, optionally, use the word "last-day" to include the last day of every month in the year.
        
  throttle:
    type: str
    description: 'Specify how much CPU to use for measurement task. Use number between 1 - 100 '

  destroy:
    type: bool
    description: 'Use this option if you want to destroy the object.'

author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
  - name: Enable Physical Capacity Reporting
    dellemc.datadomain.compression:
        state: present
      
  - name: Enable Physical Capacity Reporting and initialize
    dellemc.datadomain.compression:
        state: present
        initialize: yes

  - name: Add a new mtree to existing schedule
    dellemc.datadomain.compression:
        state: present
        schedule:
            name: schedule01
            mtrees:
                - /data/col1/mtree01
            

  - name: Add path(s) to an existing mtrees (Make sure mtree exists) and/or other parameters
    dellemc.datadomain.compression:
        state: present
        schedule:
            name: schedule01
            mtrees:
                - /data/col1/mtree03
                - /data/col1/mtree02
            priority: normal
            time: '11:00'
            day: 2

  - name: Delete mtree(s) to an existing schedule
    dellemc.datadomain.compression:
        state: absent
        schedule:
            name: schedule01
            mtrees:
                - /data/col1/mtree03


  - name: Delete (destroy) schedule if exists
    dellemc.datadomain.compression:
        state: absent
        schedule:
            name: schedule01
            
        destroy: yes

  - name: Add a new schedule
    dellemc.datadomain.compression:
        state: present
        schedule:
            name: schedule01
            mtrees:
                - /data/col1/mtree01
            priority: normal
            time: '11:00'
            day: 2

  - name: Add path(s) to an existing pathset (Make sure path exists) and/or modify measurement retention
    dellemc.datadomain.compression:
        state: present
        pathset:
            name: path02
            paths:
                - /data/col1/mtree03
                - /data/col1/mtree02
            measurement-retention: 1 # Number of days

  - name: Delete path(s) to an existing pathset
    dellemc.datadomain.compression:
        state: absent
        pathset:
            name: path02
            paths:
                - /data/col1/mtree03


  - name: Delete (destroy) pathsets if exists
    dellemc.datadomain.compression:
        state: absent
        pathset:
            name: path02
            
        destroy: yes
 
  - name: Set throttle percentage for Physical Capacity Reporting
    dellemc.datadomain.config:
        state: present
        throttle: 30 # value between <1-100>

  - name: Reset throttle percentage to default value for Physical Capacity Reporting
    dellemc.datadomain.config:
        state: absent
        throttle: '' # Value mentioned will be ignored.

'''

def check_if_object_present_absent(server, user, password, command=None, endpoint=None, failed_cmd_out=None):
    port = 22
    if command is not None:
        cmd_output = dd_connect.dd_ssh(server, user, port, command, private_key=None, password=password, header=None)
        jsonout = dd_connect.tab_to_json(output=cmd_output['output'])
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
                    obj_config[key].sort()
                    for v in value:
                        if v in obj_config[key]:
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
            if 'enable' in str(obj_config).lower():
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
        if 'destroy' in arg_dict:
            if arg_dict['destroy']:
                if 'destroy' not in modify:
                    modify.append('destroy')
        else:
            if len(obj_config_tobe) > 0:
                for key, value in obj_config_tobe.items():
                    if isinstance(value, list):
                        value.sort()
                        obj_config[key].sort()
                        for v in value:
                            if v in  obj_config[key]:
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
                if 'disabl' in str(obj_config).lower():
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


def compression():
    conditions = dict(

        compression_pathset=dict(query=dict(), req_key=['pathset'], opt_key=[], will_change=True, header=None),
        compression_schedule=dict(query=dict(), req_key=['schedule'], opt_key=[], will_change=True, header=None),
        compression_throttle=dict(query=dict(), req_key=['throttle'], opt_key=[], will_change=True, header=None),
        compression_service=dict(query=dict(), req_key=[], opt_key=[], will_change=True, header=None),
       
    )

    cmd_templates = dict(compression_pathset={'show': '["compression physical-capacity-measurement pathset show  detailed $name"]',
                                         'mod': '["compression physical-capacity-measurement pathset modify $name"]',
                                         'add':'["compression physical-capacity-measurement pathset add $name"]',
                                         'del':'["compression physical-capacity-measurement pathset del $name"]',
                                         'create': '["compression physical-capacity-measurement pathset create $name"]',
                                         'destroy': '["compression physical-capacity-measurement pathset destroy $name"]'
                                         },
                    compression_schedule={'show': '["compression physical-capacity-measurement schedule show $name"]',
                                         'mod': '["compression physical-capacity-measurement schedule modify $name"]',
                                        'add': '["compression physical-capacity-measurement schedule add $name"]',
                                        'del': '["compression physical-capacity-measurement schedule del $name"]',
                                         'create': '["compression physical-capacity-measurement schedule create $name"]',
                                         'destroy': '["compression physical-capacity-measurement schedule destroy $name"]'
                                         },
                    compression_service={'show': '["compression physical-capacity-measurement status"]',
                                            'add': '["compression physical-capacity-measurement enable"]',
                                              'del':   '["compression physical-capacity-measurement disable"]'
                                            },
                    compression_throttle={'show': '["compression physical-capacity-measurement throttle show"]',
                                            'add': '["compression physical-capacity-measurement throttle set $throttle"]',
                                                'del':    '["compression physical-capacity-measurement throttle reset"]'}
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

    conditions, cmd_templates = compression()
    fields = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'required': True},
        'initialize': {'type': 'bool', 'required': False},
        'pathset': {'type': 'dict', 'options': {'name': {'type': 'str'}, 'paths': {'type': 'list'}, 'measurement-retention': {'type': 'str'}}, 'required': False},
        'schedule': {'type': 'dict', 'options': {'name': {'type': 'str'}, 
                                                'pathsets': {'type': 'list'}, 
                                                'tenants': {'type': 'list'}, 
                                                'tenants-units': {'type': 'list'},
                                                'mtrees': {'type': 'list'},
                                                'priority': {'type': 'str', 'choices': ['normal', 'urgent']},
                                                'time': {'type': 'str'},
                                                'day': {'type': 'str'},
                                                'monthly': {'type': 'str'},

                                                }, 'required': False},
        'destroy': {'type': 'bool', 'required': False},
        'throttle': {'type': 'str'},
        'host': {'type': 'str', 'required': True},
        'port': {'type': 'int', 'default': 22},
        'username': {'type': 'str', 'required': True},
        'private_key': {'type': 'str', 'no_log': True},
        'password': {'type': 'str', 'no_log': True},
    }


    module = AnsibleModule(argument_spec=fields, mutually_exclusive=[('private_key', 'password'), ('pathset', 'schedule', 'throttle', 'initialize')],
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
    str_list_to_remove = ['day(s)']
    obj_keys = ['pathset', 'schedule']
    modify_keys = {'pathset': ['measurement-retention'], 'schedule': ['priority', 'time', 'day', 'monthly']}
    obj_key = get_obj_key(arg_dict, obj_keys)
    action = condition_check(conditions, command_build_dict=arg_dict)
    modify = ['show']
    if len(action) > 0:
        commands = build_commands(modify, action, arg_dict, modify_keys, obj_key, cmd_templates)
        command = commands[0]
        obj_exist, obj_config = check_if_object_present_absent(server, user, password, command=command, endpoint=None, failed_cmd_out=failed_cmd_out)
        obj_config = obj_config[0]
        if obj_exist:
            if obj_key == 'schedule':
                frequency = schedule_frequency(arg_dict, obj_key)
                formatted_arg_dict = modify_arg_dict_for_modify_check(arg_dict, frequency, obj_key)
                modify = check_if_modify_required(formatted_arg_dict, obj_key, obj_config, mod_keys=modify_keys ,command=None, endpoint=None)
            else:
                modify = check_if_modify_required(arg_dict, obj_key, obj_config, mod_keys=modify_keys ,command=None, endpoint=None)

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
                modify = ['create']
                commands = build_commands(modify, action, arg_dict, modify_keys, obj_key, cmd_templates)
                cmd_output['output'] = commands
                cmd_output['changed'] = False
                cmd_output['failed'] = False
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


if __name__ == '__main__':
    main()