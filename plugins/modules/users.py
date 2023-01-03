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
from ..module_utils import cmd_builder
import ansible.module_utils.common.json
import ansible.module_utils.compat.importlib
import json
from ..module_utils.cmd_templates import users
from ..module_utils.dd_connect import tab_to_json

DOCUMENTATION = r'''
---
module: users
short_description: This module is used to manage the users on datadomain
version_added: "1.0.0"
description: This module supported below actions on users
 - Create User
 - Delete User
 - Change user role
 - User enable/disable
 - set/reset user aging option
 - set/reset default aging and password strength option

options:
    state:
        description: Choose one of the below action
        type: str
        choices: [add, del, change, enable, disable, set, reset, show]
    user-name:
        description: User name
        type: str
    role-name:
        description: user role
        type: str
        choices: [admin, limited-admin, user, backup-operator, none]
    user-password:
        description: user password
        type: str
        no_log: True
    dd-password:
        description: Data domain admin or limited-admin User password 
        type: str
        no_log: True
    new-password:
        description: New user password
        type: str
        no_log: True
    aging:
        description: User password aging options.
        type: dict
        options:
            min-days-between-change:
                description: minimum days between password change
                type: str
            disable-days-after-expire:
                description: Days after which user will be expired
                type: str
            max-days-between-change:
                description: Max days between password change
                type: str
            warn-days-before-expire:
                description: Days before to generate Warning for user before expire
                type: str
    strength:
        description: Password strength options
        type: dict 
        options:
            min-length:
                description: minimum password strength
                type: str
            min-character-classes:
                description: minimum character classes
                type: str
            min-one-lowercase:
                description: minimum lowercase characters
                type: str 
                choices: ["enabled", "disabled", ""]
            min-one-uppercase:
                type: str
                description: minimum uppercase characters
                choices: ["enabled", "disabled", ""]
            min-one-digit:
                type: str
                description: minimum digit characters
                choices: ["enabled", "disabled", ""]
            min-one-special:
                type: str
                description: minimum special characters
                choices": ["enabled", "disabled", ""]
            max-three-repeat:
                type: str
                description: Max last three password repeat
                choices: ["enabled", "disabled", ""]
            passwords-remembered:
                description: Reset the number of remembered passwords to 1
                type: str 
author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
  - name:  Add a new user
    dellemc.datadomain.users:
        state: add
        user-name: boostuser04
        role-name: admin
        user-password: password01
        dd-password: password02

  - name:  Change the password for a user
    dellemc.datadomain.users:
        state: change
        user-name: boostuser04
        new-password: password04
        user-password: password01
        dd-password: password02


  - name: Change the role of a user
    dellemc.datadomain.users:
        state: change
        user-name: boostuser04
        role-name: user

  - name:  Remove a user
    dellemc.datadomain.users:
        state: del
        user-name: boostuser04


  - name:  Disable the user's account
    dellemc.datadomain.users:
        state: disable
        user-name: boostuser04

  - name:  Enable the user's account
    dellemc.datadomain.users:
        state: enable
        user-name: boostuser04

  - name: Reset the default password aging policy
    dellemc.datadomain.users:
        state: reset
        aging:
            min-days-between-change: ""
            max-days-between-change: ""
            warn-days-before-expire: ""
            disable-days-after-expire: ""

  - name: Set the default password aging policy
    dellemc.datadomain.users:
        state: set
        aging:
            min-days-between-change: 999
            max-days-between-change: 9999
            warn-days-before-expire: 9998
            disable-days-after-expire: 10000}


  - name:  Reset the password aging policy for a user
    dellemc.datadomain.users:
        state: reset
        user-name: boostuser04
        aging:
            min-days-between-change: ""
            max-days-between-change: ""
            warn-days-before-expire: ""
            disable-days-after-expire: ""

  - name:  Set the password aging policy for a user
    dellemc.datadomain.users:
        state: reset
        user-name: boostuser04
        aging:
            min-days-between-change: 999
            max-days-between-change: 9999
            warn-days-before-expire: 9998
            disable-days-after-expire: 10000


  - name:  Reset the password strength policy to defaults
    dellemc.datadomain.users:
        state: reset
        user-name: boostuser04
        strength:
            min-length: ""
            min-character-classes: ""
            min-one-lowercase: ""
            min-one-uppercase: ""
            min-one-digit: ""
            min-one-special: ""
            max-three-repeat: ""
            passwords-remembered: ""

  - name:  Set the password strength policy
    dellemc.datadomain.users:
        state: reset
        user-name: boostuser04
        strength:
            min-length: 10
            min-character-classes: 2
            min-one-lowercase: enabled
            min-one-uppercase: disabled
            min-one-digit: enabled
            min-one-special: enabled
            max-three-repeat: enabled
            passwords-remembered: 2
'''


def main():
    conditions, supported_commands = users()
    fields = {
        'state': {'type': 'str', 'choices': ['add', 'del', 'change', 'enable', 'disable', 'set', 'reset', 'show']},
        'user-name': {'type': 'str'},
        'role-name': {'type': 'str', 'choices': ['admin', 'limited-admin', 'user', 'backup-operator', 'none']},
        'user-password': {'type': 'str', 'no_log': True},
        'dd-password': {'type': 'str', 'no_log': True},
        'new-password': {'type': 'str', 'no_log': True},
        'aging': {'type': 'dict', 'options': {'min-days-between-change': {'type': 'int'},
                                              'disable-days-after-expire': {'type': 'int'},
                                              'max-days-between-change': {'type': 'int'},
                                              'warn-days-before-expire': {'type': 'int'}}},
        'strength': {'type': 'dict', 'options': {'min-length': {'type': 'str'},
                                                 'min-character-classes': {'type': 'str'},
                                                 'min-one-lowercase': {'type': 'str',
                                                                       "choices": ["enabled", "disabled", ""]},
                                                 'min-one-uppercase': {'type': 'str',
                                                                       "choices": ["enabled", "disabled", ""]},
                                                 'min-one-digit': {'type': 'str',
                                                                   "choices": ["enabled", "disabled", ""]},
                                                 'min-one-special': {'type': 'str',
                                                                     "choices": ["enabled", "disabled", ""]},
                                                 'max-three-repeat': {'type': 'str',
                                                                      "choices": ["enabled", "disabled", ""]},
                                                 'passwords-remembered': {'type': 'str'}}},
        'host': {'type': 'str', 'required': True},
        'port': {'type': 'int', 'default': 22},
        'username': {'type': 'str', 'required': True},
        'private_key': {'type': 'str', 'no_log': True},
        'password': {'type': 'str', 'no_log': True},
    }
    module = AnsibleModule(

        argument_spec=fields, mutually_exclusive=[('private_key', 'password')],
                           required_one_of=[('private_key', 'password')]

    )

    arg_dict = {}
    for key, value in module.params.items():
        if value is not None:
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
    # command, will_change, is_filter, header = cmd_builder.build_command(action=action, arg_dict=arg_dict, supported_commands=supported_commands, conditions=conditions)
    # arg_dict['command'] = command
    # module.exit_json(failed=False, msg=arg_dict, changed=changed)
    if len(action) > 0:
        command, will_change, is_filter, header = cmd_builder.build_command(action=action, arg_dict=arg_dict, supported_commands=supported_commands, conditions=conditions)
        cmd_output = cmd_builder.run_cmd(module=module, command=command, is_filter=is_filter, server=server,
                                         user=user, port=port, private_key=private_key, password=password, header=header)
        changed = will_change
        if 'show' in str(command):
            jsonout = tab_to_json(cmd_output['output'], header)
            cmd_output['output'] = jsonout
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
