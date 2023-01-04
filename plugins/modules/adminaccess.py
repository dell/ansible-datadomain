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
from ..module_utils import dd_connect
import ansible.module_utils.common.json
import ansible.module_utils.compat.importlib
import json
from ..module_utils.cmd_templates import adminaccess

DOCUMENTATION = r'''
---

module: adminaccess
short_description: 'Run adminaccess command'
description: 'This module will help to run adminaccess commands on datadomain'
version_added: '2.0.0'
options:
  state:
    type: str
    choices:
    - enable, disable, show
    required: true
    description: 'Choose the state as per the action you want to perform'
  service:
    type: str
    choices:
    - http, https, ftp, ftps, telnet, ssh, scp, web-service, all
    description: 'This attribute specifies the services you want to toggle'
author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
- name: enable the https access on data domain
  dellemc.datadomain.adminaccess:
      state: enable
      service: https

- name: show attributes of all servies
  dellemc.datadomain.adminaccess:
      state: show
'''


def main():
    conditions, supported_commands = adminaccess()
    fields = {
        'state': {'type': 'str', 'choices': ['enable', 'disable', 'show'], 'required': True},
        'service': {'type': 'str', 'choices': ['http', 'https', 'ftp', 'ftps', 'telnet', 'ssh', 'scp', 'web-service', 'all']},
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
    changed = False
    action = cmd_builder.condition_check(conditions=conditions, command_build_dict=arg_dict)
    if len(action) > 0:
        command, will_change, is_filter, header = cmd_builder.build_command(action=action, arg_dict=arg_dict,
                                                                    supported_commands=supported_commands,
                                                                    conditions=conditions)
        changed = will_change
        cmd_output = cmd_builder.run_cmd(module=module, command=command, is_filter=is_filter, server=server,
                                         user=user, port=port, private_key=private_key, password=password, header=header)
        if 'show' in str(command):
            jsonout = dd_connect.tab_to_json(cmd_output['output'], header)
            cmd_output['output'] = jsonout
    else:
        state = arg_dict['state']
        possible_options = {}
        for key, value in conditions.items():
            if conditions[key]['state'] == state:
                possible_options = conditions[key]
        meta = ''
        meta_output.append(eval(str(meta)))
        module.fail_json(msg=f'Possible Action(s) based on state "{state}" {possible_options}')

    module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=changed)


if __name__ == '__main__':
    main()
