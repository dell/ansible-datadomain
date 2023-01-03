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
from ..module_utils.cmd_templates import compression

DOCUMENTATION = r'''
module: compression
short_description: This module is used to manage the PCM compression on datadomain
version_added: "3.0.0"
description: This module supported below actions on CIFS services
  compression schedule enable
  compression schedule disable
  compression status
  compression schedule destroy
  compression schedule modify
  compression schedule del
  compression schedule create
  compression schedule add
  compression sample stop
  compression sample start
  compression throttle set
  compression throttle show
  compression throttle reset
options:
  state: 
    type: str
    choices:
        - enable, disable, status, start, stop, add, del, create, destroy, modify, set, reset, show
    required: true
    description: 'Use this option to mention the action you want to run. Choices supported are status, enable, disable'
  sample:
    type: dict
    description: 'Use this option to start/stop the PCM measurement sample.'
    option:
      pathsets:
        type: list
        description: 'Type the pathset names in list format'
      tenants:
        type: list
        description: 'Type the tenants names in list format'
      tenants-units:
        type: list
        description: 'Type the tenants-unit names in list format'
      mtrees:
        type: list
        description: 'Type the mtree names in list format'
      priority:
        type: str
        description: 'Select one of the priority to start the sample'
        choices:
            - normal
            - urgent
  initialize:
    type: bool
    description: 'Use this option when you want to enable and initialize the pcm.' 
  schedule:
    type: dict
    description: 'Use this option to create, delete, enable, disable or destroy schedule'
    option:
      name:
        type: str
        description: 'Type the name of the schedule'
      pathsets:
        type: list
        description: 'Type the pathset names in list format'
      tenants:
        type: list
        description: 'Type the tenant names in list format'
      tenants-units:
        type: list
        description: 'Type the tenant-unit names in list format'
      mtrees:
        type: list
        description: 'Type the mtree names in list format'
      priority:
        type: str
        description: 'select the priority to start the scheduled measurement task'
        choices:
            - normal
            - urgent
      time:
        type: str
        description: 'Type the schedule start time in 24 hour format e.g. 13:00' 
      day:
        type: list
        description: 'With the keyword day, specify days as the days of the week using either lowercase, three letter abbreviations for the days of the week: mon, tue, wed, thu, fri, sat, sun, or as integers: 0 = Sunday, 1 = Monday, 2 = Tuesday, 3 = Wednesday, 4 = Thursday, 5 = Friday, 6 = Saturday'
      monthly:
        type: str
        description: Specify the days of the month using integers (1-31) and, optionally, use the word "last-day" to include the last day of every month in the year.

  throttle:
    type: str
    description: 'Specify how much CPU to use for measurement task. Use number between 1 - 100 '
auther:
  - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
  - name: Disable PCM
    dellemc.datadomain.compression:
        state: disable
        
  - name: Eanble PCM
    dellemc.datadomain.compression:
        state: enable

  - name: Eanble and initialize PCM
    dellemc.datadomain.compression:
        state: enable
        initialize: true
        
  - name: Start the sample task for perticular mtree
    dellemc.datadomain.compression:
        state: start
        sample:
            mtrees:
                - /data/col1/mtreename01

   - name: Stop the sample task for perticular mtree
    dellemc.datadomain.compression:
        state: stop
        sample: 
            mtrees:
                - /data/col1/mtreename01

  - name: Start the sample task for perticular mtree
    dellemc.datadomain.compression:
        state: start
        sample:
            mtrees:
                 /data/col1/mtreename01
  
  - name: Create the PCM schedule
    dellemc.datadomain.compression:
        state: create
        schedule: 
            mtrees: 
                - /data/col1/mtreename01
                - /data/col1/mtreename02
            priority: normal
            time: 10:00
            day:
                - sun
                - mon
                - tue		

  - name: Delete entities from a compression physical-capacity-measurement schedule
    dellemc.datadomain.compression:
        state: del
        schedule: 
            mtrees:
                - /data/col1/mtreename01

  - name: Destroy a schedule
    dellemc.datadomain.compression:
        state: destroy
        schedule: 
            name: test_schedule

  - name: Disable a schedule
    dellemc.datadomain.compression:
        state: disable
        schedule: 
            name: test_schedule
  
  - name: Enable a schedule
    dellemc.datadomain.compression:
        state: enable
        schedule: 
            name: test_schedule

  - name: Add a new compression physical-capacity-measurement schedule
    dellemc.datadomain.compression:
        state: modify
        schedule: 
            name: test_schedule
            priority: normal
            time: 12:00

  - name: Show Physical Capacity Reporting enable or disable status
    dellemc.datadomain.compression:
        state: status
        
  - name: Reset throttle percentage for Physical Capacity Reporting to the default value
    dellemc.datadomain.compression:
        state: reset
        throttle: '' # default value is 20 percentage


  - name: Set throttle percentage for Physical Capacity Reporting
    dellemc.datadomain.compression:
        state: set
        throttle: 50

  - name: Show throttle percentage for Physical Capacity Reporting
    dellemc.datadomain.compression:
        state: show
        throttle: ''
               
'''


def main():
    conditions, supported_commands = compression()
    fields = {
        'state': {'type': 'str', 'choices': ['enable', 'disable', 'status', 'start', 'stop', 'add', 'del', 'create', 'destroy', 'modify', 'set', 'reset', 'show'], 'required': True},
        'initialize': {'type': 'bool'},
        'sample': {'type':'dict', 'option': {'pathsets': {'type': 'list'},
                                             'tenants': {'type': 'list'},
                                             'tenants-units': {'type': 'list'},
                                             'mtrees': {'type': 'list'},
                                             'priority': {'type': 'str', 'choices': ['normal', 'urgent']},
                                             }},
        'schedule': {'type': 'dict', 'option': {'name': {'type': 'str'},
                                                'pathsets': {'type': 'list'},
                                              'tenants': {'type': 'list'},
                                              'tenants-units': {'type': 'list'},
                                              'mtrees': {'type': 'list'},
                                              'priority': {'type': 'str', 'choices': ['normal', 'urgent']},
                                                'time': {'type': 'str'},
                                                'day': {'type': 'list'},
                                                'monthly': {'type': 'str'},
                                                }},
        'throttle': {'type': 'str'},
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
        command = [command[0].replace("name", "")]
        changed = will_change
        cmd_output = cmd_builder.run_cmd(module=module, command=command, is_filter=is_filter, server=server,

                                         user=user, port=port, private_key=private_key, password=password)
        if 'schedule show' in str(command):
            jsonout = dd_connect.tab_to_json(cmd_output['output'], header)
            cmd_output['output'] = jsonout
                                         
        # if 'schedule show' in str(command):
        #     jsonout = dd_connect.tab_to_json(cmd_output['output'], header)
        #     cmd_output['output'] = jsonout
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
