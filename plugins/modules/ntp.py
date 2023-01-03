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
from ..module_utils.cmd_templates import ntp


DOCUMENTATION = r'''
---
module: ntp
short_description: This module is used to manage the NTP
version_added: "1.0.0"
description: This module supported below actions on NTP
    ntp add timeserver $timeserver
    ntp del timeserver $timeserver
    ntp reset timeserver
    ntp enable
    ntp disable
    ntp reset
    ntp sync
    ntp status
options:
    state:
        description: Select the option as per action you want to perform
        type: str
        choices: [add, del, enable, disable, reset, sync, status]
        required: True
    timeserver:
        description: Time server IP or hostname
        type: str

author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
  - name: Add one or more remote time servers
    dellemc.datadomain.ntp:
        state: add
        timeserver: 10.5.0.2 10.5.0.3

  - name: Delete one or more remote time servers
    dellemc.datadomain.ntp:
        state: del
        timeserver: 10.5.0.3

  - name: Disable the NTP local server
    dellemc.datadomain.ntp:
        state: disable

  - name: enable the NTP local server
    dellemc.datadomain.ntp:
        state: enable

  - name: Reset (to default) the NTP server configuration
    dellemc.datadomain.ntp:
        state: reset

  - name: Reset (to default) remote time servers
    dellemc.datadomain.ntp:
        state: reset
        timeserver: ''

  - name: Show the local NTP server status
    dellemc.datadomain.ntp:
        state: status

  - name: Sync with a configured NTP server
    dellemc.datadomain.ntp:
        state: sync
'''


def main():
    conditions, supported_commands = ntp()
    fields = {
        'state': {'type': 'str', 'choices': ['add', 'del', 'enable', 'disable', 'reset', 'sync', 'status', 'show'], 'required': True},
        'timeserver': {'type': 'str'},
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
        command, will_change, is_filter, header = cmd_builder.build_command(action=action, arg_dict=arg_dict, supported_commands=supported_commands, conditions=conditions)
        cmd_output = cmd_builder.run_cmd(module=module, command=command, is_filter=is_filter, server=server,
                                         user=user, port=port, private_key=private_key, password=password, header=header)
        changed = will_change
    else:
        state = arg_dict['state']
        possible_options = {}
        for key, value in conditions.items():
            if conditions[key]['state'] == state:
                possible_options = conditions[key]
        cmd_output['output'] = possible_options
        cmd_output['failed'] = True
    module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=changed)


if __name__ == '__main__':
    main()
