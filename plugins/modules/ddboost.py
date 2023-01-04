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
sys.path.insert(0, '/usr/share/ansible')
from ..module_utils import dd_connect
from ..module_utils import cmd_builder
import ansible.module_utils.common.json
import ansible.module_utils.compat.importlib
import json
from ..module_utils.cmd_templates import ddboost

DOCUMENTATION = r'''
---
module: ddboost
short_description: This module is used to manage the ddboost protocol on datadomain
version_added: "1.0.0"
description: This module supported below actions on ddboost protocol
    ddboost storage-unit create $storage_unit user $user_name
    ddboost storage-unit delete $storage_unit
    ddboost storage-unit modify $storage_unit user $user_name
    ddboost storage-unit rename $storage_unit $new_storage_unit
    ddboost storage-unit undelete $storage_unit
    ddboost user assign $user_name
    ddboost user unassign $user_name
    ddboost status
    ddboost enable
    ddboost disable
options:
    state: 
        description: Specify the action 
        type: str
        choices: ['modify', 'rename', 'enable', 'disable', 'status', 'undelete', 'assign', 'unassign', 'create', 'delete']
    storage-unit:
        description: Storage Unit name
        type: str
    new-storage-unit: 
        description: Use this option with rename. Specify new storage unit name
        type: str
    user-name:
        description: Username to assign to ddboost protocol or storage unit
        type: str
    quota: 
        description: Use below options to specify the quota on storage unit 
        type: dict
        suboptions: 
            quota-soft-limit:
                description: Soft quota limit in format <n> [MiB| GiB|TiB|PiB] e.g. 10 GiB 
                type: str
            quota-hard-limit: 
                description: Hard quota limit in format <n> [MiB| GiB|TiB|PiB] e.g. 100 GiB
                type: str
            report-physical-size:
                description: physical report size in format <n> [MiB| GiB|TiB|PiB]
                type: str
    stream-limit: 
        description: Use these options to specify stream limit on Read, write, replication read and write.  Use number or none to specify no limit
        type: dict
        suboptions: 
            write-stream-soft-limit:
                description: specify soft limit for number of streams for write.
                type: str
            read-stream-soft-limit:
                description: specify soft limit for number of streams for write
                type: str
            repl-stream-soft-limit:
                description: specify soft limit for number of streams for replication
                type: str
            combined-stream-soft-limit:
                description: specify soft limit for number of streams for all read write and replication
                type: str
            combined-stream-hard-limit:
                description: specify soft limit for number of streams for all read write and replication
                type: str
author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
  - name: Enable ddboost
    dellemc.datadomain.ddboost:
        state: enable

  - name: Disable ddboost
    dellemc.datadomain.ddboost:
        state: disable

  - name: Create the ddboost storage unit
    dellemc.datadomain.ddboost:
        state: create
        storage-unit: a001us034nve001
        user-name: a001booost
        ## Optional parameters
        quota:
            quota-soft-limit: 10 GiB
            quota-hard-limit: 15 GiB
            report-physical-size: 10 GiB
        stream-limit:
            write-stream-soft-limit: 10 # or none - remove limit
            read-stream-soft-limit: 15 # or none - remove limit
            repl-stream-soft-limit: 13 # or none - remove limit
            combined-stream-soft-limit: 20 # or none - remove limit
            combined-stream-hard-limit: 20 # or none - remove limit		

  - name: Delete the ddboost storage unit
    dellemc.datadomain.ddboost:
        state: delete
        storage-unit: a001us034nve001

  - name: Modify ddboost user on storage unit or Quota and/or stream-limit settings
    dellemc.datadomain.ddboost:
        state: modify
        storage-unit: a001us034nve001
        user-name: a001boost
        ## Optional parameters
        quota:
            quota-soft-limit: 10 GiB
            quota-hard-limit: 15 GiB
            report-physical-size: 10 GiB
        stream-limit:
            write-stream-soft-limit: 10 # or none - remove limit
            read-stream-soft-limit: 15 # or none - remove limit
            repl-stream-soft-limit: 13 # or none - remove limit
            combined-stream-soft-limit: 20 # or none - remove limit
            combined-stream-hard-limit: 20 # or none - remove limit	

  - name: Rename ddboost storage unit to new name
    dellemc.datadomain.ddboost:
        state: rename
        storage-unit: a001us034nve001
        new-storage-unit: a001us034nve001-rep

  - name: Undelete the ddboost storage unit
    dellemc.datadomain.ddboost:
        state: undelete
        storage-unit: a001us034nve0

  - name: Assign the username to the ddboost protocol
    dellemc.datadomain.ddboost:
        state: assign
        user-name: a001boost

  - name: unassign the username from the ddboost protocol
    dellemc.datadomain.ddboost:
        state: unassign
        user-name: a001boost

  - name: Status of ddboost protocol
    dellemc.datadomain.ddboost:
        state: status

'''


def main():
    conditions, supported_commands = ddboost()
    fields = {
        'state': {'type': 'str', 'choices':['modify', 'rename', 'enable', 'disable', 'status', 'undelete', 'assign', 'unassign', 'create', 'delete']},
        'storage-unit': {'type': 'str'},
        'new-storage-unit': {'type': 'str'},
        'user-name': {'type': 'str'},
        'quota': {'type': 'dict', 'options': {'quota-soft-limit': {'type': 'str'}, 'quota-hard-limit': {'type': 'str'}, 'report-physical-size': {'type': 'str'}}},
        'stream-limit': {'type': 'dict', 'options': {'write-stream-soft-limit': {'type': 'str'},
                                                     'read-stream-soft-limit': {'type': 'str'},
                                                      'repl-stream-soft-limit': {'type': 'str'},
                                                      'combined-stream-soft-limit': {'type': 'str'},
                                                      'combined-stream-hard-limit': {'type': 'str'}}},
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
        changed = will_change
        cmd_output = cmd_builder.run_cmd(module=module, command=command, is_filter=is_filter, server=server,
                                         user=user, port=port, private_key=private_key, password=password, header=header)
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
