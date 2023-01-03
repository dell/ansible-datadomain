# Copyright ©️ 2022 Dell Inc. or its subsidiaries.
from __future__ import (absolute_import, division,
                        print_function)
from ansible.module_utils.basic import AnsibleModule
from ..module_utils.dd_connect import tab_to_json

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
from ..module_utils.cmd_templates import mtree

DOCUMENTATION = '''
---
module: mtree
short_description: This module is used to manage the Mtrees on Data domain
version_added: "1.0.0"
description: This module supported below actions on Mtrees
    mtree alias create $alias_name mtree $mtree_path
    mtree create $mtree_path
    mtree alias delete $alias_name
    mtree delete $mtree_path
    mtree rename $mtree_path $new_mtree_path
    mtree modify $mtree_path tenant-unit $tenant_unit
    mtree option set anchoring-algorithm $anchoring_algorithm mtree $mtree_path
    mtree option set app-optimized-compression $app_optimized_compression mtree $mtree_path
    mtree option set randomio $randomio mtree $mtree_path
    mtree option reset anchoring-algorithm mtree $mtree_path
    mtree option reset app-optimized-compression mtree $mtree_path
    mtree option reset randomio mtree $mtree_path
    mtree retention-lock enable mode $retention_lock mtree $mtree_path
    mtree retention-lock disable mtree $mtree_path
    mtree retention-lock set $retention mtree $mtree_path
    mtree retention-lock reset $retention mtree $mtree_path
    mtree undelete $mtree_path

options:
    state:
        description: 
            - Use state for the action you want to perform
        type: str
        choices: [create, delete, rename, enable, disable, set, reset, show, undelete]
        required: true
    mtree-path:
        description: Mtree Path
        type: str
    new-mtree-path:
        description: New Mtree Path when you want to rename the mtree
        type: str
    alias-name:
        description: Mtree Alias name
        type: str
        choices: [admin, limited-admin, user, backup-operator, none]
    tenant-unit:
        description: Tenant unit name
        type: str
    anchoring-algorithm:
        description: Algorithm type
        type: str
        choices: [variable, fixed, ""]
    app-optimized-compression:
        description: app optimized compression
        type: str
        choices: [none, global, oracle1]
    randomio:
        description: random io settings
        type: str
        choices: [enable, disable]
    retention-lock:
        description: retention lock type
        type: str
        choices: [compliance, governance, ""]
    quota:
        description: quota settings for mtree
        type: dict
        options: 
            quota-soft-limit:
                description: Soft limit format n MiB | GiB | TiB| PiB
                type: str
            quota-hard-limit:
                description:  Hard limit format n MiB | GiB | TiB| PiB
                type: str
    retention:
        description: Retention lock settings for retention period
        type: dict
        options: 
            min-retention-period:
                description: Minimum retention periods format 720Minutes | days
                type: str
            max-retention-period:
                description: Max retention period format 720Minutes | days
                type: str
            automatic-retention-period:
                description: Automatic retention period format 720Minutes | days
                type: str
            automatic-lock-delay:
                description: automatic retention lock delay format 120Minutes
                type: str

author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
  - name: Get the list of MTrees
    dellemc.datadomain.mtree:
        state: list
        
  - name: Create a MTree
    dellemc.datadomain.mtree:
        state: create
        mtree-path: /data/col1/a001us043nve001
        quota:
            quota-soft-limit: 10 GiB
            quota-hard-limit: 12 GiB

  - name: Delete a MTree
    dellemc.datadomain.mtree:
        state: delete
        mtree-path: /data/col1/a001us043nve001


  - name: Rename a MTree
    dellemc.datadomain.mtree:
        state: rename
        mtree-path: /data/col1/a001us043nve001
        new-mtree-path: /data/col1/a001us043nve002

  - name:  Set anchoring-algorithm
    dellemc.datadomain.mtree:
        state: set
        mtree-path: /data/col1/a001us043nve001
        anchoring-algorithm: variable

  - name:   Disables retention-lock for specified MTree.
    dellemc.datadomain.mtree:
        state: disable
        mtree-path: /data/col1/a001us043nve001
        retention-lock: ""

  - name:  Enables retention-lock for specified MTree.
    dellemc.datadomain.mtree:
        state: enable
        mtree-path: /data/col1/a001us043nve001
        retention-lock: compliace

  - name:  Reset retention periods to default for specified MTree.
    dellemc.datadomain.mtree:
        state: reset
        mtree-path: /data/col1/a001us043nve001
        retention:
            min-retention-period: ""

  - name:  Set retention periods for specified MTree.
    dellemc.datadomain.mtree:
        state: set
        mtree-path: /data/col1/a001us043nve001
        retention:
            min-retention-period: 720Minuets 

  - name: Undelete a MTree
    dellemc.datadomain.mtree:
        state: undelete
        mtree-path: /data/col1/a001us043nve001  - name: Create a MTree
'''


def main():
    conditions, supported_commands = mtree()
    fields = {
        'state': {'type': 'str',
                  'choices': ['create', 'delete', 'rename', 'enable', 'disable', 'set', 'reset', 'list', 'undelete']},
        'mtree-path': {'type': 'str'},
        'new-mtree-path': {'type': 'str'},
        'alias-name': {'type': 'str', 'choices': ['admin', 'limited-admin', 'user', 'backup-operator', 'none']},
        'tenant-unit': {'type': 'str'},
        'anchoring-algorithm': {'type': 'str', 'choices': ['variable', 'fixed', ""]},
        'app-optimized-compression': {'type': 'str', 'choices': ['none', 'global', 'oracle1']},
        'randomio': {'type': 'str', 'choices': ['enable', 'disable']},
        'retention-lock': {'type': 'str', 'choices': ['compliance', 'governance', ""]},
        'quota': {'type': 'dict',
                  'options': {'quota-soft-limit': {'type': 'str'}, 'quota-hard-limit': {'type': 'str'}}},
        'retention': {'type': 'dict', 'options': {'min-retention-period': {'type': 'str'},
                                                  'max-retention-period': {'type': 'str'},
                                                  'automatic-retention-period': {'type': 'str'},
                                                  'automatic-lock-delay': {'type': 'str'}}},
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
                                         user=user, port=port, private_key=private_key, password=password)
        if 'mtree list' in str(command):
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
        changed = False
    module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=changed)


if __name__ == '__main__':
    main()
