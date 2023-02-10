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
from ..module_utils.cmd_templates import nfs


DOCUMENTATION = r'''
---
module: nfs
short_description: This module is used to manage the NFS protocol on datadomain
version_added: "1.0.0"
description: This module supported below actions on NFS
    nfs export add $export_name clients $client_list
    nfs export del $export_name clients $client_list
    nfs disable
    nfs enable
    nfs export create $export_name path $path clients $client_list
    nfs export destroy $export_name
    nfs export modify $export_name clients $client-list options $export_options
    nfs export rename $export_name $new_export_name
    nfs reset clients
    nfs restart
    nfs status
options:
    state:
        description: Use following option for the action you want to take
        type: str
        choices: [add, del, create, destroy, enable, disable, modify, rename, reset, set, restart, status]
        required: True
    path:
        description: mtree or directory path on the data domain
        type: str
    client-list:
        description: list of clients to allow access to export
        type: str

    version:
        description: NFS Version
        type: str
    export-name: 
        description: Export name
        type: str
    new-export-name:
        description: new export name
        type: str
    export-options:
        description: export options like 'rw,no_root_squash,no_all_squash,secure'
        type: str
author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''

  - name: Disable NFS clients from connecting
    dellemc.datadomain.nfs:
        state: disable
        
  - name: Enable NFS clients to connect
    dellemc.datadomain.nfs:
        state: enable

  - name: Add a client to an export
    dellemc.datadomain.nfs:
        state: add
        export-name: backupserver01
        client-list: 10.0.0.6 10.0.0.7
 
  - name: Create an export, optionally add clients
    dellemc.datadomain.nfs:
        state: create
        export-name: backupserver01
        path: /data/col1/backupserver01
        client-list: 10.0.0.3 10.0.0.4
        export-options: 'rw,no_root_squash,no_all_squash,secure'
                                       

  - name: remove a client from an export
    dellemc.datadomain.nfs:
        state: del
        export-name: backupserver01
        client-list: 10.0.0.6 10.0.0.7								   
  
  - name: Destroy and export
    dellemc.datadomain.nfs:
        state: destroy
        export-name: backupserver01

  - name: Modify an export, clients and/or export options
    dellemc.datadomain.nfs:
        state: create
        export-name: backupserver01
        path: /data/col1/backupserver01
        client-list: 10.0.0.3 10.0.0.4
        export-options: 'rw,no_root_squash,no_all_squash,secure'

  - name: Rename an export
    dellemc.datadomain.nfs:
        state: rename
        export-name: backupserver01
        new-export-name: backupserver02
 
 
  - name: Reset (to default) the NFS client list
    dellemc.datadomain.nfs:
        state: reset

  - name: Restart NFS servers
    dellemc.datadomain.nfs:
        state: restart
        version: 4 # OPtiona field. Also you can type All to 

  
  - name: Restart NFS servers
    dellemc.datadomain.nfs:
        state: status
'''


def main():
    conditions, supported_commands = nfs()
    fields = {
        'state': {'type': 'str', 'choices': ['add', 'del', 'create', 'destroy', 'enable', 'disable', 'modify',
                                             'rename', 'reset', 'set', 'restart', 'status', 'show'], 'required': True},
        'path': {'type': 'str'},
        'clients': {'type': 'str'},
        'option-list': {'type': 'str'},
        'version': {'type': 'str'},
        'export-name': {'type': 'str'},
        'new-export-name': {'type': 'str'},
        'export-options': {'type': 'str'},
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
