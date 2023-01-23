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
from ..module_utils.cmd_templates import config


DOCUMENTATION = r'''
---
module: config
short_description: This module is used to manage the config on datadomain
version_added: "1.0.0"
description: This module supported below actions 
  - config set admin-email $admin_email
  - config set admin-host $admin_host
  - config set location $location
  - config set mailserver $mailserver
  - config set timezone $timezone
  - config reset admin-email
  - config reset admin-mail
  - config reset location
  - config reset mailserver
  - config reset timezone

options:
    state:
        description: Use this option to mention the action you want to run. Choices supported are 'reset', 'set'
        required: true
        type: str
        choices:
          - set, reset
    option: 
        description: Here mention which configuration item you want to work with. 
        type: str
        choices: ['admin-email', 'admin-host', 'location', 'mailserver', 'timezone']
        required: false
    admin-email: 
        description: Specify the admin email address here. 
        type: str
        required: false
    admin-host:
        description: Specify the admin host ip or hostname
        type: str
        required: false
    location:
        description: Specify the location of data domain. like DC or rack location
        type: str
        required: false    
    mailserver:
        description: specify the mail server ip or hostname
        type: str
        required: false
    timezone: 
        description: Timezone names begin with Africa, America, Antarctica, Asia, Atlantic, Australia, Brazil, Canada, Chile, Europe, Indian, Mexico, Mideast, Pacific and US
        type: str
        required: false
author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''

- name: Reset (to default) admin-email
  dellemc.datadomain.config
    state: reset
    option: admin-email

- name: Reset (to default) admin-host
  dellemc.datadomain.config
    state: reset
    option: admin-host

- name: Reset (to default) location
  dellemc.datadomain.config
    state: reset
    option: location


- name: Reset (to default) mailserver
  dellemc.datadomain.config
    state: reset
    option: mailserver		

- name: Reset (to default) timezone
  dellemc.datadomain.config
    state: reset
    option: timezone	

- name: Reset (to default) admin-host
  dellemc.datadomain.config
    state: reset
    option: admin-host

- name: Reset (to default) location
  dellemc.datadomain.config
    state: reset
    option: location


- name: Reset (to default) mailserver
  dellemc.datadomain.config
    state: reset
    option: mailserver		

- name: Reset (to default) timezone
  dellemc.datadomain.config
    state: reset
    option: timezone		


- name: Set email address for alerts, detailed-autosupport and daily alert summary emails
  dellemc.datadomain.config
    state: set
    option: admin-email
    admin-email: abc@abc.com


- name: Set the administrative host
  dellemc.datadomain.config
    state: set
    option: admin-host
    admin-host: servername

- name: Set the administrative host
  dellemc.datadomain.config
    state: set
    option: location
    location: DCID # This could be RACK location


- name: Set the mail (SMTP) server
  dellemc.datadomain.config
    state: set
    option: mailserver
    mailserver: 10.5.23.3 # SMTP server IP/hostname


- name: Set the timezone 
  dellemc.datadomain.config
    state: set
    option: timezone
    timezone: US/Pacific # Timezone names begin with Africa, America, Antarctica,
                                   Asia, Atlantic, Australia, Brazil, Canada, Chile, Europe, Indian, Mexico,
                                   Mideast, Pacific and US

'''


def main():
    conditions, supported_commands = config()
    fields = {
        'state': {'type': 'str', 'choices': ['reset', 'set'], 'required': True},
        'option': {'type':'str', 'choices': ['admin-email', 'admin-host', 'location', 'mailserver', 'timezone']},
        'admin-email': {'type': 'str'},
        'admin-host': {'type': 'str'},
        'location': {'type': 'str'},
        'mailserver': {'type': 'str'},
        'timezone': {'type': 'str'},
        'host': {'type': 'str', 'required': True},
        'port': {'type': 'int', 'default': 22},
        'username': {'type': 'str', 'required': True},
        'private_key': {'type': 'str', 'no_log': True},
        'password': {'type': 'str', 'no_log': True},
    }


    module = AnsibleModule(argument_spec=fields, mutually_exclusive=[('private_key', 'password')],
                           required_one_of=[('private_key', 'password')])

    meta_output = []
    arg_dict = {}
    for key, value in module.params.items():
        if value is not None:
            dict_value = {}
            if isinstance(value, dict):
                for k, v in value.items():
                    if v is not None:
                        dict_value[k] = v
                arg_dict[key] = dict_value
            else:
                arg_dict[key] = value
    server = module.params['host']
    user = module.params['username']
    port = module.params['port']
    private_key = module.params['private_key']
    password = module.params['password']
    keys_to_delete = ['host', 'username', 'private_key', 'password']
    for key in keys_to_delete:
        if key in arg_dict:
            del arg_dict[key]

    cmd_output = {}
    changed = False
    action = cmd_builder.condition_check(conditions=conditions, command_build_dict=arg_dict)
    if len(action) > 0:
        command, will_change, is_filter, header = cmd_builder.build_command(action=action, arg_dict=arg_dict,
                                                                    supported_commands=supported_commands,
                                                                    conditions=conditions)
        changed = will_change
        cmd_output = cmd_builder.run_cmd(module=module, command=command, is_filter=is_filter, server=server,
                                         user=user, port=port, private_key=private_key, password=password, header=header)
    else:
        state = arg_dict['state']
        possible_options = {}
        for key, value in conditions.items():
            if conditions[key]['query']['state'] == state:
                possible_options[key] = conditions[key]
        cmd_output['output'] = possible_options
        cmd_output['failed'] = True

    module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=changed)


if __name__ == '__main__':
    main()

