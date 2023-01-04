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
from ..module_utils.cmd_templates import filesys


DOCUMENTATION = r'''
---
module: filesys
short_description: This module is used to manage the filesystem on datadomain
version_added: "1.0.0"
description: This module supported below actions on filesys
    filesys enable
    filesys create
    filesys clean reset $clean
    filesys clean set $clean
    filesys clean start
    filesys clean stop
    filesys encryption abort-apply-changes
    filesys encryption apply-changes
    filesys encryption $encryption reset
    filesys encryption embedded-key-manager set key-rotation-policy $key_rotation_policy
    filesys encryption key-manager set $external_key_manager
    filesys encryption key-manager set key-rotation-policy $key_rotation_policy
    filesys encryption algorithm set $algorithm
    filesys encryption embedded-key-manager reset key-rotation-policy
    filesys encryption $encryption keys create
    filesys encryption key-manager disable
    filesys encryption key-manager enable
    filesys encryption disable
    filesys encryption enable
    filesys encryption keys delete
    filesys encryption keys destroy
    filesys encryption keys sync
    filesys fastcopy source $filecopy_source destination $filecopy_destination
    filesys status
options:
    state:
        description: Use the one of the action to perform. 
        type: str
        choices: [enable, disable, status, set, reset, status, abort, apply, modify, abort-apply-changes, apply-changes, start, stop, create, delete, destroy, sync]
        required: True
    option:
        description: Specify which attribute of filesys you want to work on
        type: str
        choices: [encryption, clean, fastcopy]
    encryption:
        description: use one of the Encryption type 
        type: str
        choices: [algorithm, embedded-key-manager, key-manager]
    algorithm:
        description: Specify the algorithm
        type: str
        choices: [aes_128_cbc, aes_256_cbc, aes_128_gcm, aes_256_gcm]
    key-rotation-policy:
        description: Specify the key rotation policy. format - every <n> weeks or months or none
        type: str
    tier:
        description: Specify storage tier
        type: str
        choices: [active, cloud-unit, all]
    external-key-manager:
        description: Following attributes of external key manager
        type: dict
        suboptions:
            server:
                description: Key manager server
                type: str
            port:
                description: Specify port
                type: int
            fips-mode:
                description: fips mode enabled or disabled
                type: str
                choices: [enabled, disabled]
            key-class:
                description: specify key class
                type: str
            server-type:
                description: Server Type from below choices
                type: str
                choices: [keysecure, rkm]
            kmip-user:
                description: KMIP user
                type: str
    key-id:
        description: Key ID to work with. Use either Keyid or MUid
        type: str
    muid:
        description: MUID to work with. Use either Keyid or MUid
        type: str
    ext-key-manager-state:
        description: ext key manager state - deactivated
        type: str
    fastcopy-source:
        description: Fastcopy Source Mtree path
        type: str
    fastcopy-destination:
        description: Fastcopy destination Mtree path
        type: str
    clean:
        description: Filesystem cleaning schedule and throttle
        type: dict
        suboptions:
            schedule:
                description: Schedule cleaning never or daily <time> or <day(s)> <time> or biweekly <day> <time> or monthly <day(s)> <time>
                type: str
            throttle:
                description: Specify the CPU throttle percentage in number like 40 
                type: int
            all:
                description: Use only when state is reset. This will reset both Schedule and Throttle to default values
                type: str
author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
  - name:  Reset (to default) the schedule/Throttle/all (both)
    dellemc.datadomain.filesys:
        state: reset
        operation: clean
        clean:
            schedule: "" # use throttle or all

  - name:  Set the Schedule
    dellemc.datadomain.filesys:
        state: set
        operation: clean
        clean:
            schedule: daily 11:00

  - name:  Set (to default) the Throttle
    dellemc.datadomain.filesys:
        state: set
        operation: clean
        clean:
            throttle: 60

  - name:  Start the cleaning
    dellemc.datadomain.filesys:
        state: start
        operation: clean

  - name:  Check clean status
    dellemc.datadomain.filesys:
        state: status
        operation: clean

  - name:  Stop the cleaning operation
    dellemc.datadomain.filesys:
        state: stop
        operation: clean

  - name:  Creates a filesystem with the active tier storage
    dellemc.datadomain.filesys:
        state: create
 
  - name:  Enable file system operations
    dellemc.datadomain.filesys:
        state: enable
        
  - name:   Abort previously issued apply-changes request
    dellemc.datadomain.filesys:
        state: abort-apply-changes
        operation: encryption
                                      
                                       
  - name:  Reset the encryption algorithm to default (aes_256_cbc)
    dellemc.datadomain.filesys:
        state: reset
        operation: encryption
        encryption: algorithm

    - name: Set the encryption algorithm [aes_128_cbc | aes_256_cbc | aes_128_gcm | aes_256_gcm]
    dellemc.datadomain.filesys:
        state: set
        operation: encryption
        encryption: algorithm
        algorithm: aes_128_gcm
                                                    

  - name:  Apply current encryption configuration to filesystem
    dellemc.datadomain.filesys:
        state: apply-changes
        operation: encryption

   - name:  Disable encryption
    dellemc.datadomain.filesys:
        state: disable
        operation: encryption
        tier: active  #optional parameter [active | cloud-unit {<unit-name> | all}]

  - name:  Create a new key
    dellemc.datadomain.filesys:
        state: create
        operation: encryption
        encryption: embedded-key-manager

  - name:  Reset key-rotation-policy of embedded-key-manager.
    dellemc.datadomain.filesys:
        state: reset
        operation: encryption
        encryption: embedded-key-manager
                                      
  - name:  Setup key-rotation-policy of embedded-key-manager
    dellemc.datadomain.filesys:
        state: set
        operation: encryption
        encryption: embedded-key-manager
        key-rotation-policy: 10
                                       

  - name:  Enable encryption
    dellemc.datadomain.filesys:
        state: enable
        operation: encryption
        tier: active # #optional parameter [active | cloud-unit {<unit-name> | all}]

  - name:  Disable RKM/KeySecure
    dellemc.datadomain.filesys:
        state: disable
        operation: encryption
        encryption: key-manager

  - name:  Enable RKM/KeySecure
    dellemc.datadomain.filesys:
        state: enable
        operation: encryption
        encryption: key-manager
                                       
  - name:  Create a new external key manager key
    dellemc.datadomain.filesys:
        state: create
        operation: encryption
        encryption: key-manager
                                       

  - name:  Reset key manager attributes
    dellemc.datadomain.filesys:
        state: reset
        operation: encryption
        encryption: key-manager
                                       
  - name:  Reset key-rotation-policy of external key manager.
    dellemc.datadomain.filesys:
        state: reset
        operation: encryption
        encryption: key-manager
        key-rotation-policy: ""
                                       

  - name:  Set key-rotation-policy of external key manager
    dellemc.datadomain.filesys:
        state: set
        operation: encryption
        encryption: key-manager
        key-rotation-policy: every 1 month # format - every <n> {weeks | months} | none
                                       

  - name:  Mark the key as deleted
    dellemc.datadomain.filesys:
        state: delete
        operation: encryption
        key-id: 1 # use one of <key-id> | muid <key-muid>
        tier: active # #optional parameter [active | cloud-unit {<unit-name> | all}]

  - name:  Mark the key as destroyed
    dellemc.datadomain.filesys:
        state: delete
        operation: encryption
        key-id: 1 # use one of <key-id> | muid <key-muid>
        tier: active # #optional parameter [active | cloud-unit {<unit-name> | all}]
                
                                       
  - name: Sync the keys with the Key Manager
    dellemc.datadomain.filesys:
        state: sync
        operation: encryption
 
  - name: Create External Key Manager
    dellemc.datadomain.filesys:
        state: set
        operation: encryption
        encryption: key-manager
        external-key-manager:
            server: 10.15.150.19
            port: 2125
            fips-mode: enabled
            server-type: keysecure
            key-class: classic
            kmip-user: sudarshan

'''


def main():
    conditions, supported_commands = filesys()
    fields = {
        'state': {'type': 'str', 'choices': ['enable', 'disable', 'status', 'set', 'reset', 'status', 'abort', 'apply',
                                             'modify', 'abort-apply-changes', 'apply-changes', 'start', 'stop',
                                             'create', 'delete', 'destroy', 'sync'],
                  'required': True},
        'operation': {'type': 'str', 'choices': ['encryption', 'clean', 'fastcopy']},
        'encryption': {'type': 'str', 'choices': ['algorithm', 'embedded-key-manager', 'key-manager']},
        'algorithm': {'type': 'str', 'choices':['aes_128_cbc', 'aes_256_cbc', 'aes_128_gcm', 'aes_256_gcm']},
        'key-rotation-policy': {'type': 'str'},
        'tier': {'type': 'str', 'choices': ['active', 'cloud-unit', 'all']},
        'external-key-manager': {'type': 'dict', 'options': {
            'server': {'type': 'str'},
            'port': {'type': 'int'},
            'fips-mode': {'type': 'str', 'choices': ['enabled', 'disabled']},
            'key-class': {'type': 'str'},
            'server-type': {'type': 'str', 'choices': ['keysecure', 'rkm']},
            'kmip-user':  {'type': 'str'},
        }},
        'key-id': {'type': 'str'},
        'muid': {'type': 'str'},
        'ext-key-manager-state': {'type': 'str'},
        'fastcopy-source': {'type': 'str'},
        'fastcopy-destination': {'type': 'str'},
        'clean': {'type': 'dict', 'options': {
            'schedule': {'type': 'str'}, 'throttle': {'type': 'str'}, 'all': {'type': 'str'}}},
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
            if conditions[key]['state'] == state:
                possible_options = conditions[key]
        cmd_output['output'] = possible_options
        cmd_output['failed'] = True
    module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=changed)


if __name__ == '__main__':
    main()
