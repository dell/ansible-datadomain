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


DOCUMENTATION = r'''
---
module: config
short_description: This module is used to manage the configuration using config command.
version_added: "1.0.0"
description: This module can be used if you want to set or reset timezone, email id, admin host, mailserver, location on datadomain. Please note that, if you want to reset the configuration, then use state absent with option. If you specify value for that option, module will check if that value is set, if not set, it wont do reset.
  
options:
  state:
    type: str
    choices:
    - present, absent
    required: true
    description: 'Choose the option from the choices above'
  config:
    type: str
    choices:
    - admin-email, admin-host, location, mailserver, timezone
    required: true
    description: 'Type one of the configuration from the list.'
  value:
    type: str
    description: 'Required if you use state as present.'
author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
  - name: Set email address
    dellemc.datadomain.config:
        state: present
        config: admin-email
        value: user.name@company.com
        
  - name: Reset email address
    dellemc.datadomain.config:
        state: absent
        config: admin-email

'''

def get_config(server, user, password, arg_dict):
    command = f"config show {arg_dict['config']}"
    port=22
    cmd_output = dd_connect.dd_ssh(server, user, port, command, private_key=None, password=password, header=None)
    jsonout = dd_connect.tab_to_json(cmd_output['output'], header=None)
    cmd_output['output'] = jsonout
    for key, value in jsonout[0].items():
        if arg_dict['state'] == 'present':
            if value == arg_dict['value']:
                modify = False
            else:
                modify = True
        elif arg_dict['state'] == 'absent':
            if 'value' in arg_dict and arg_dict['value'] is not None:
                if value == arg_dict['value']:
                    modify = True
                else:
                    modify = False
            else:
                modify = True
        else:
            modify = None

    return modify


def modify_config(server, user, password, arg_dict):
    port=22
    cmd_dict = {'present': 'set', 'absent': 'reset'}
    state = arg_dict['state']
    if arg_dict['state'] == 'present':
        command = f'config set {arg_dict["config"]} {arg_dict["value"]}'
    else:
        command = f'config reset {arg_dict["config"]}'

    cmd_output = dd_connect.dd_ssh(server, user, port, command, private_key=None, password=password, header=None)
    return cmd_output


def main():

    conditions, supported_commands = adminaccess()
    fields = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'required': True},
        'config': {'type': 'str', 'choices': ['admin-email', 'admin-host', 'location', 'mailserver', 'timezone'], 'required': True},
        'value': {'type': 'str', 'required': False},
        'host': {'type': 'str', 'required': True},
        'port': {'type': 'int', 'default': 22},
        'username': {'type': 'str', 'required': True},
        'private_key': {'type': 'str', 'no_log': True},
        'password': {'type': 'str', 'no_log': True},
    }


    module = AnsibleModule(argument_spec=fields, mutually_exclusive=[('private_key', 'password')],
                           required_one_of=[('private_key', 'password')], required_if=[('state', 'present', ('config', 'value'), False)])
    
    server = module.params['host']
    user = module.params['username']
    port = module.params['port']
    private_key = module.params['private_key']
    password = module.params['password']
    meta_output = []
    arg_dict = {}
    for key, value in module.params.items():
        if value is not None:
            arg_dict[key] = value
    keys_to_delete = ['host', 'username', 'private_key', 'password']
    for key in keys_to_delete:
        if key in arg_dict:
            del arg_dict[key]
    cmd_output = {}
    
    modify = get_config(server, user, password, arg_dict)

    
    if modify:
        command_output = modify_config(server, user, password, arg_dict)
        if not command_output['failed']:
            cmd_output['output'] = command_output['output']
            cmd_output['changed'] = True
            cmd_output['failed'] = False
        else:
            cmd_output['output'] = command_output['output']
            cmd_output['changed'] = False
            cmd_output['failed'] = True
    else:
        serv_state = arg_dict['state']
        cmd_output['output'] = f"{arg_dict['config']} {arg_dict['value']} is {arg_dict['state']}. No action needed."
        cmd_output['changed'] = False
        cmd_output['failed'] = False


    module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=cmd_output['changed'])


if __name__ == '__main__':
    main()