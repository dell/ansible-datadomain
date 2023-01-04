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
from ..module_utils.cmd_templates import replication


DOCUMENTATION = r'''
---
module: replication
short_description: This module is used to manage the replication
version_added: "1.0.0"
description: This module supported below actions for replication

    replication add 
    replication break 
    replication disable 
    replication enable 
    replication initialize 
    replication modify 
    replication option reset
    replication option set
    replication resync
    replication sync
    replication status

options:
  state:
    type: str
    choices:
    - enable, disable, add, break, modify, resync, sync, initialize, status, show,
      set, reset, recover
    required: true
    description: 'Select from options for your action'
  source:
    type: str
    description: 'Replication source Mtree in format mtree://<ddhostname><mtree path>'
  destination:
    type: str
    description: 'Replication destination Mtree in format mtree://<ddhostname><mtree path>'
  low-bw-optim:
    type: str
    choices:
    - enabled, disabled
    description: 'Low bandwidth optimization'
  encryption:
    type: dict
    description: 'Encryption'
    suboptions:
      state:
        type: str
        choices:
        - enabled, disabled
        description: 'Use this parameter to enable or disable encryption'
      authentication-mode:
        type: str
        choices:
        - one-way, two-way, anonymous
        description: 'auth mode only when Encryption is enabled'
  propagate-retention-lock:
    type: str
    choices:
    - enabled, disabled
    description: 'Propogate Retention lock from source mtree to replicated mtree'
  crepl-gc-bw-optim:
    type: str
    choices:
    - enabled, disabled
    description: ''
  ipversion:
    type: str
    choices:
    - ipv4, ipv6
    description: 'ipversion'
  max-repl-streams:
    type: int
    description: 'maximum replication streams'
  destination-tenant-unit:
    type: str
    description: 'Destination Tenant Unit name'
  option:
    type: dict
    description: 'Replication option settings'
    suboptions:
      bandwidth:
        type: str
        description: 'Set the network bandwidth (Bps) for thedes restorer'
      delay:
        type: str
        description: 'Set the network delay (ms) for the restorer'
      listen-port:
        type: str
        description: 'Set the listen port for the restorer'
      default-sync-alert-threshold:
        type: str
        description: 'Set the sync-time (in hrs) when alert is raised'
      enforce-fips-compliance:
        type: str
        choices:
        - enabled, disabled
        description: 'Enforce FIPS compliance mode'
  repl-port:
    type: int
    description: 'Specify port to be used for replication'
  connection-host:
    type: str
    description: 'Specify IP of the remote data domain for replication'
  source-host:
    type: str
    description: 'Use when you modify the source host of replication context'
  destination-host:
    type: str
    description: 'Use when you modify the destination host of replication context'

        
author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
 
  - name: Add a replication pair
    dellemc.datadomain.replication:
        state: add
        source: mtree://source.datadomain.name/data/col1/source
        destination: mtree://destination.datadomain.name/data/col1/destination
        #optional parameters
        low-bw-optim: enabled
        encryption: 
            state: enabled
            authentication-mode: one-way # This option only used when encryption is enabled.
        propagate-retention-lock: enabled
        ipversion: ipv4
        max-repl-streams: 5

  - name: break  and remove replication to the specified destination
    dellemc.datadomain.replication:
        state: break
        destination: mtree://destination.datadomain.name/data/col1/destination

  - name: Disable replication
    dellemc.datadomain.replication:
        state: disable
        destination: mtree://destination.datadomain.name/data/col1/destination
                                 
  - name: Enable replication
    dellemc.datadomain.replication:
        state: enable
        destination: mtree://destination.datadomain.name/data/col1/destination

  - name: Initialize replication on the source
    dellemc.datadomain.replication:
        state: initialize
        destination: mtree://destination.datadomain.name/data/col1/destination
                         
  - name: Reconfigure replication context for new source host
    dellemc.datadomain.replication:
        state: modify
        destination: mtree://destination.datadomain.name/data/col1/destination
        connection-host: 10.0.0.1

  - name: Reconfigure replication context for low bandwidth optimization
    dellemc.datadomain.replication:
        state: modify
        destination: mtree://destination.datadomain.name/data/col1/destination
        low-bw-optim: enabled

  - name: Reconfigure replication context for low bandwidth optimization
    dellemc.datadomain.replication:
        state: set
        option:
            bandwidth: 50 #Set the network bandwidth (Bps) for the des restorer
            delay: 100 #Set the network delay (ms) for the restorer

  - name: Resynchronize replication between the source and destination
    dellemc.datadomain.replication:
        state: resync
        destination: mtree://destination.datadomain.name/data/col1/destination

'''


def main():
    conditions, supported_commands = replication()
    fields = {
        'state': {'type': 'str', 'choices': ['enable', 'disable', 'add', 'break', 'modify', 'resync', 'sync', 'initialize', 'status', 'show', 'set', 'reset', 'recover'],
                  'required': True},
        'source': {'type': 'str'},
        'destination': {'type': 'str'},
        'low-bw-optim': {'type': 'str', 'choices':['enabled', 'disabled']},
        'encryption': {'type': 'dict', 'options':{
                                            'state': {'type': 'str', 'choices': ['enabled', 'disabled']},
                                            'authentication-mode': {'type': 'str', 'choices': ['one-way', 'two-way', 'anonymous']},
                                            }},
        
        'propagate-retention-lock': {'type': 'str', 'choices':['enabled', 'disabled']},
        'crepl-gc-bw-optim' : {'type': 'str', 'choices':['enabled', 'disabled']},
        'ipversion': {'type': 'str', 'choices':['ipv4', 'ipv6']},
        'max-repl-streams': {'type': 'int'},
        'destination-tenant-unit': {'type': 'str'},
        'option': {'type': 'dict', 'options': {
                            'bandwidth': {'type': 'str'}, 
                            'delay': {'type': 'str'},
                            'listen-port': {'type': 'str'},
                            'default-sync-alert-threshold': {'type': 'str'},
                            'enforce-fips-compliance': {'type': 'str', 'choices':['enabled', 'disabled']}
        }},
        'repl-port': {'type': 'int'},
        'connection-host': {'type': 'str'},
        'source-host': {'type': 'str'},
        'destination-host': {'type': 'str'},
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
        if 'show' in str(command):
            jsonout = dd_connect.tab_to_json(cmd_output['output'], header)
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
