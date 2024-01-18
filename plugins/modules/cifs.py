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
from ..module_utils.action import cifs


DOCUMENTATION = r'''
---
module: cifs
short_description: This module is used to manage the CIFS services on datadomain
version_added: "1.0.0"
description: This module supported below actions on CIFS services
  - cifs enable
  - cifs disable
  - cifs share create
  - cifs share modify
  - cifs share enable
  - cifs share disable
  - cifs share destroy
  
options:
  state:
    type: str
    choices:
    - present, absent
    required: true
    description: 'Choose the option from the choices above'
  share:
    type: str
    description: 'Type the share name'
  path:
    type: str
    description: 'Type the path of the directory. it should start with /backup or /ddvar'
  comment:
    type: str
    description: 'Type comment for the share.'
  max-connections:
    type: str
    description: 'Maximum connections'
  destroy:
    type: bool
    description: 'If combined with absent state, it will delete the share.'
  clients:
    type: list
    description: 'Client IPs who can access the share. Type "*" if you want to allow all hosts (not recommemded)'
  users:
    type: list
    description: 'Type user names who can access the share'
  groups:
    type: list
    description: 'Type group names who can access the share'
author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
  - name: Disable CIFS
    dellemc.datadomain.cifs:
        state: absent

  - name: enable CIFS
    dellemc.datadomain.cifs:
        state: present

  - name: Create CIFS Share
    dellemc.datadomain.cifs:
        state: present
        share: share_ddfs
        path: /backup
        clients: '*'

  - name: Modify CIFS Share to add client ip if present.
    dellemc.datadomain.cifs:
        state: present
        share: share_ddfs
        clients: 
          - 10.0.0.2

  - name: Modify CIFS Share to remove client ip if exists.
    dellemc.datadomain.cifs:
        state: absent
        share: share_ddfs
        clients: 
          - 10.0.0.2

  - name: Disable CIFS Share.
    dellemc.datadomain.cifs:
        state: present
        share: share_ddfs

  - name: Enable cifs share.
    dellemc.datadomain.cifs:
        state: absent
        share: share_ddfs

  - name: Destroy cifs share.
    dellemc.datadomain.cifs:
        state: absent
        share: share_ddfs  
        destroy: true   
'''

def check_share(server, user, password, endpoint):
  command_outout = dd_connect.dd_requests(server=server, user=user, api_pass=password, endpoint=endpoint, request_type="get", payload=None)
  if not command_outout['failed']:
    share_exists = True
  else:
    share_exists = False
  return dict(share_exists=share_exists, share_details=command_outout['output'])


def cifs_toggle(server, user, password, endpoint, cmd_output, arg_dict, payload=None):
  command_outout = dd_connect.dd_requests(server=server, user=user, api_pass=password, endpoint=endpoint, request_type="get", payload=payload)
  if "enabled" in str(command_outout['output']) and arg_dict['state'] == "present":
    cmd_output['output'] = command_outout['output']
    cmd_output['failed'] = command_outout['failed']
    if command_outout['failed']:
      cmd_output['changed'] = False
    else:
      cmd_output['changed'] = False
  elif "enabled" in str(command_outout['output']) and arg_dict['state'] == "absent":
    endpoint = "/api/v1/dd-systems/0/protocols/cifs/disable"
    command_outout = dd_connect.dd_requests(server=server, user=user, api_pass=password, endpoint=endpoint, request_type="post", payload=payload)
    cmd_output['output'] = command_outout['output']
    cmd_output['failed'] = command_outout['failed']
    if command_outout['failed']:
      cmd_output['changed'] = True
    else:
      cmd_output['changed'] = False
  elif "disabled" in str(command_outout['output']) and arg_dict['state'] == "present":
    endpoint = "/api/v1/dd-systems/0/protocols/cifs/enable"
    command_outout = dd_connect.dd_requests(server=server, user=user, api_pass=password, endpoint=endpoint, request_type="post", payload=payload)
    cmd_output['output'] = command_outout['output']
    cmd_output['failed'] = command_outout['failed']
    if command_outout['failed']:
      cmd_output['changed'] = True
    else:
      cmd_output['changed'] = False
  elif "disabled" in str(command_outout['output']) and arg_dict['state'] == "absent":
    cmd_output['output'] = command_outout['output']
    cmd_output['failed'] = command_outout['failed']
    if command_outout['failed']:
      cmd_output['changed'] = False
    else:
      cmd_output['changed'] = False
  else:
    cmd_output['output'] = "No Condition matched."
    cmd_output['failed'] = False
    cmd_output['changed'] = False


def share_create(server, user, password, endpoint, arg_dict, cmd_output):
  req_keys = ['share', 'path']
  optional_keys = ['client', 'user', 'max_connections', 'group', 'comment']
  keys_check = []
  missing_args = []
  payload = {}
  del_keys = ['port', 'state', 'destroy', 'disable']
  for key in req_keys:
    if key not in arg_dict:
      keys_check.append(False)
      missing_args.append(key)
    else:
      keys_check.append(True)
  if not all(keys_check):
    missing_args = str(missing_args).replace("[", "").replace("]", "")
    cmd_output['output'] = f"Below arguments are required and not mentioned - {missing_args}. Please resubmit the playbook after specifying these keys"
    cmd_output['failed'] = True
    cmd_output['changed'] = False
  else:
    for key, value in arg_dict.items():
      if key == 'share':
        payload['name'] = value
      else:
        if key not in del_keys:
          payload[key] = value
    payload = json.dumps(payload)
    # payload = json.loads(payload)
    command_outout = dd_connect.dd_requests(server=server, user=user, api_pass=password, endpoint=endpoint, request_type="post", payload=payload)
    cmd_output['output'] = command_outout['output']
    cmd_output['failed'] = command_outout['failed']
    if command_outout['failed']:
      cmd_output['changed'] = False
    else:
      cmd_output['changed'] = True


def share_modify(server, user, password, endpoint, arg_dict, cmd_output, share_details):
  mod_keys = ['clients', 'groups', 'users', 'max_connections']
  option_values = {}
  for key in share_details["share_details"]["option"]:
    if key["key"] not in option_values:
      option_values[key["key"]] = []
    option_values[key["key"]].append(key["value"])
  payload = {} 
  key_present = []
  if "destroy" not in arg_dict:
    request_type = "put"
    for key in mod_keys:
      if key in arg_dict:
        key_present.append(True)
        if isinstance(arg_dict[key], list):
          payload[key] = []
          for val in arg_dict[key]:
            if arg_dict['state'] == "absent":
              if key in option_values:
                if val in option_values[key]:
                  v = {"name": val, "delete": True}
                else:
                  v = None
            else:
              v = {"name": val}
            if v is not None:
              payload[key].append(v)
        else:
          payload[key] = arg_dict[key]
      else:
        key_present.append(False)
    if not any(key_present):
      if arg_dict['state'] == "absent":
        payload["disable"] = True
      else:
        payload["disable"] = False
  else:
    if arg_dict['state'] == "absent":
      payload = None
      request_type = "delete"
    else:
      payload = None
      request_type = "get"
  if payload is not None:
    payload = json.dumps(payload)
  if request_type != "get":
    command_outout = dd_connect.dd_requests(server=server, user=user, api_pass=password, endpoint=endpoint, request_type=request_type, payload=payload)
    cmd_output['output'] = command_outout['output']
    cmd_output['failed'] = command_outout['failed']
    if cmd_output['failed']:
        cmd_output['changed'] = False
    else:
      cmd_output['changed'] = True
  else:
    cmd_output['output'] = "Invalid Request. Please check playbook and rerun"
    cmd_output['failed'] = False
    cmd_output['changed'] = False

def main():

    conditions, supported_commands = cifs(status=False)
    fields = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'required': True},
        'share': {'type': 'str'},
        'path': {'type': 'str'},
        'max-connections': {'type': 'str'},
        'clients': {'type': 'list'},
        'users': {'type': 'list'},
        'groups': {'type': 'list'},
        'comment': {'type': 'text'},
        'destroy': {'type': 'bool'},
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
    action, check_status_ep = cmd_builder.condition_check(conditions=conditions, command_build_dict=arg_dict)
    shares = []
    if len(action) > 0:
      if check_status_ep is not None:
        if action == "cifs_share_create":
          endpoint = f"{check_status_ep}/{arg_dict['share']}"
          share_details = check_share(server, user, password, endpoint)
          if not share_details['share_exists']:
            endpoint = f"{check_status_ep}"
            share_create(server, user, password, endpoint, arg_dict, cmd_output)
          else:
            share_modify(server, user, password, endpoint, arg_dict, cmd_output, share_details)
        elif action == "cifs_share_modify":
          endpoint = f"{check_status_ep}/{arg_dict['share']}"
          share_details = check_share(server, user, password, endpoint)
          if share_details['share_exists']:
            share_modify(server, user, password, endpoint, arg_dict, cmd_output, share_details)
          else:
            cmd_output["output"] = f"Share '{arg_dict['share']}' does not exist."
            cmd_output["failed"] = False
            cmd_output["changed"] = False
        elif action == "cifs_enable" or action == "cifs_disable":
          endpoint = f"{check_status_ep}"
          cifs_toggle(server, user, password, endpoint, cmd_output, arg_dict)
        else:
          cmd_output['output'] = "As per playbook condition, no action matched. Please re-check documentation and rerun the playbook"
          cmd_output['failed'] = False
          cmd_output['changed'] = False

    module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=cmd_output['changed'])


if __name__ == '__main__':
    main()
