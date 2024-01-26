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
module: adminaccess
short_description: This module can be used to manage the services using adminaccess command.
version_added: "1.0.0"
description: All configurations using adminaccess command are not supported. This module only supports enable/disable of services like http, https, ftp, ftps, telnet, ssh, scp, web-service. 
  
options:
  state:
    type: str
    choices:
    - present, absent
    required: true
    description: 'Choose the option from the choices above'
  service:
    type: str
    choices:
    - http, https, ftp, ftps, telnet, ssh, scp, web-service
    required: true
    description: 'Type one of the service name from the list.'
 
author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
  - name: Disable service
    dellemc.datadomain.adminaccess:
        state: absent
        service: http 
        
  - name: Enable service
    dellemc.datadomain.adminaccess:
        state: present
        service: http 
'''

def service_status(server, user, password, arg_dict):
    command = 'adminaccess show'
    port=22
    cmd_output = dd_connect.dd_ssh(server, user, port, command, private_key=None, password=password, header=None)
    jsonout = dd_connect.tab_to_json(cmd_output['output'], header=None)
    cmd_output['output'] = jsonout
    status_dict = {"yes": "present", "no": "absent"}
    for service in jsonout:
        try:
            if service['Service'] == arg_dict['service']:
                enabled = service['Enabled']
                if arg_dict['state'] == status_dict[enabled]:
                    modify = False
                    break
                else:
                    modify = True
                    break
            else:
                modify = None
        except KeyError:
            pass
    return modify

def modify_service(server, user, password, command):
    port=22
    cmd_output = dd_connect.dd_ssh(server, user, port, command, private_key=None, password=password, header=None)
    return cmd_output


def main():

    conditions, supported_commands = adminaccess()
    fields = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'required': True},
        'service': {'type': 'str', 'choices': ['http', 'https', 'ftp', 'ftps', 'telnet', 'ssh', 'scp', 'web-service'], 'required': True},
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
        if value is not None:
            arg_dict[key] = value
    keys_to_delete = ['host', 'username', 'private_key', 'password']
    for key in keys_to_delete:
        if key in arg_dict:
            del arg_dict[key]
    cmd_output = {}
    
    action, check_status_ep = cmd_builder.condition_check(conditions=conditions, command_build_dict=arg_dict)
    status_dict = {'present': 'Enabled', 'absent': 'Disabled'}
    modify = service_status(server, user, password, arg_dict)

    if len(action) > 0:
        if modify:
            command = supported_commands[action] + " " + arg_dict['service']
            command_output = modify_service(server, user, password, command)
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
            cmd_output['output'] = f"Service {arg_dict['service']} is already {status_dict[serv_state]}. No action needed."
            cmd_output['changed'] = False
            cmd_output['failed'] = False

    else:
        cmd_output['output'] = "As per playbook condition, no action matched. Please re-check documentation and rerun the playbook"
        cmd_output['failed'] = False
        cmd_output['changed'] = False

    module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=cmd_output['changed'])


if __name__ == '__main__':
    main()