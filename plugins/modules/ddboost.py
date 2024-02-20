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
from ..module_utils.action import adminaccess
from string import Template
import copy
import re

DOCUMENTATION = r'''
---
module: ddboost
short_description: This module enables you to manage ddboost protocol
version_added: "1.0.0"
description: This module enables you to create, modify, delete storage units and assign/unassign users.
  
options:
state:
  type: str
  choices:
  - present
  - absent
  required: true
  description: Use one of the above option
storage-unit:
  type: str
  required: false
  description: Storage Unit Name
tenant-unit:
  type: str
  required: false
  description: Tenant unit name
new_storage_unit:
  type: str
  required: false
  description: Use this option when you want to rename storage unit
user:
  type: list
  required: false
  description: User name
skip-chown:
  type: bool
  required: false
  description: if True, it will skip changing ownership of files.

author:
    - Sudarshan Kshirsagar (@kshirs1)
'''

EXAMPLES = r'''
    - name: Enable DD Boost
      dellemc.datadomain.net:
        state: present
    
    - name: Disable DD Boost
      dellemc.datadomain.net:
        state: absent
    
    - name: Create ddboost storage unit
      dellemc.datadomain.net:
        state: present
        storage_unit: storageunit01
        user: boostuser

    - name: Modify storage-unit user
      dellemc.datadomain.net:
        state: present
        storage_unit: storageunit01
        user: boostuser
        skip-chown: True # if skip-chown is not mentioned, default value is False

    - name: Modify storage-unit user
      dellemc.datadomain.net:
        state: present
        storage_unit: storageunit01
        user: boostuser

    - name: Rename storage-unit
      dellemc.datadomain.net:
        state: present
        storage_unit: storageunit01
        new_storage_unit: storageunit02

    - name: Delete storage-unit
      dellemc.datadomain.net:
        state: absent
        storage_unit: storageunit01

    - name: Assign user to DDboost user list
      dellemc.datadomain.net:
        state: present
        user: boostuser
    
    - name: Assign user to DDboost user list
      dellemc.datadomain.net:
        state: absent
        user: boostuser			
'''


def tab_to_json(output, header=None):
    final_data = []
    if "--" in str(output) and "Option" not in str(output) and '- share' not in str(output):
        commandOut = output.split('\n')
        lookup = "--"
        i = 0
        p = 0
        out = {}
        data_frames = []
        for line in commandOut:
            i += 1
            if lookup in line:
                out[p] = i - 1
                p += 1
        p = 0
        total_lines = len(out) - 1
        if total_lines == 0:
            out[1] = out[0] + 2
            total_lines = 1
        while p < total_lines:
            start_line = out[p] + 1
            p += 1
            end_line = out[p]
            data_frames.append(commandOut[start_line:end_line])
        for line in data_frames:
            for l in line:
                data = {}
                obj = re.split('\s\s\s+', l.strip())
                i = 0
                if len(obj) >= (len(header) - 1):
                    for o in obj:
                        data[header[i]] = o
                        i = i + 1
                    final_data.append(data)
        return final_data
    elif "Option" in str(output) and 'Value' in str(output):
        cmdOutput = output.split('\n\n')
        for section in cmdOutput:
            data = {}
            section = section.strip()
            lines = section.split('\n')

            if ':' in lines[0]:
                mkey = lines[0].strip().replace(':', '')
                data[mkey] = {}
                for line in lines[1:]:
                    if '--' not in line and 'Option' not in line:
                        key, value = re.split('\s\s+', line.strip())
                        data[mkey][key] = value
                final_data.append(data)
            else:
                mkeys = re.split('\s\s+', lines[0].strip())
                if 'Option' in mkeys:

                    for line in lines[1:]:

                        if '--' not in line and len(line) > 0:
                            data = {}
                            key, value = re.split('\s\s+', line.strip())
                            data[key] = value
                            final_data.append(data)
                else:
                    for line in lines[1:]:
                        data = {}
                        if '--' not in line and 'Option' not in line:
                            values = re.split('\s\s+', line.strip())
                            i = 0
                            for value in values:
                                data[mkeys[i]] = value
                                i += 1
                            final_data.append(data)
        return final_data
    elif ': ' in str(output):
        cmdOutput = output.split('\n\n')
        for line in cmdOutput:
            if len(line.strip()) > 0:
                obj = line.split('\n')
                data = {}
                for o in obj:
                    
                    if ":" in o:
                        key, value = o.split(":", 1)

                        if len(value.strip()) > 0:
                            data[key.strip().lower().replace(' ', '_')] = value.strip()
                        else:
                            data[key.strip().lower().replace(' ', '_')] = []
                    else:
                        if len(o) > 0 and '*' not in o:

                            try:
                                key, value = re.split('\s\s+', o.strip())
                                data[key.lower().replace(' ', '_')] = value.strip()
                            except Exception as e:
                                data[key.strip().lower().replace(' ', '_')].append(o.strip())
                                pass

                final_data.append(data)
        return final_data
    else:
        data = {}
        data['output'] = []
        cmdOutput = output.split('\n')
        for line in cmdOutput:
            if len(line) > 0:
                data['output'].append(line)
        final_data.append(data)
        return final_data


def ddboost():
    conditions = dict(
        storage_unit=dict(query=dict(), req_key=['storage_unit'], opt_key=[], will_change=True, header=None),
        user=dict(query=dict(), req_key=['user'], opt_key=[], will_change=True, header=None),
        ddboost_service=dict(query=dict(), req_key=[], opt_key=[], will_change=True, header=None))
    
    command_template = dict(storage_unit={'show': '["ddboost storage-unit show"]',
                                         'create':'["ddboost storage-unit create $storage_unit user $user"]',
                                         'modify':'["/rest/v2.0/dd-systems/0/protocols/ddboost/storage-units/$storage_unit"]',
                                         'del':'["ddboost storage-unit delete $storage_unit"]',
                                         'rename':'["ddboost storage-unit rename $storage_unit $new_storage_unit"]',
                                         'undel':'["ddboost storage-unit undelete $storage_unit"]',
                                         },

                            user={'show': '["ddboost user show"]',
                                         'assign':'["ddboost user assign $user"]',
                                         'unassign':'["ddboost user unassign $user"]',
                                         },
                            
                            ddboost_service={'show': '["ddboost status"]',
                                         'enable': '["ddboost enable"]',
                                         'disable': '["ddboost disable"]',
                                         },
                                         )
    
    headers = dict(user=['user', 'token_access'],
                    storage_unit=['storage_unit', 'pre_comp_gib', 'status', 'user', 'report_physical'],
                    ddboost_service=None,
                    
                    )
    rename_keys = dict()
    return conditions, command_template, headers, rename_keys


def condition_check(conditions, command_build_dict):
    diff_keys = []
    action = ''
    query_out = []
    for key, value in conditions.items():
        query_out = []
        diff_keys = []
        for obj in conditions[key]['req_key']:
            if obj not in command_build_dict:
                diff_keys.append(obj)
        if len(diff_keys) == 0:
            for query_key, query_value in conditions[key]['query'].items():
                try:
                    if command_build_dict[query_key] == query_value:
                        query_out.append(True)
                    else:
                        query_out.append(False)
                except KeyError:
                    query_out.append(False)
                    pass
            if all(query_out):
                action = key
                try:
                    check_status_ep = value['check_status_ep']
                except KeyError:
                    check_status_ep=None   
                break
    return action


def get_obj_key(arg_dict, obj_keys):
    for obj in obj_keys:
        if obj in arg_dict:
            return obj
            break


def build_commands(modify, action, arg_dict, obj_key, cmd_templates, config_to_modify=None):
    commands = {}
    payload = {}
    # if obj_key is None:
    #     obj_key = []


    narg_dict = copy.deepcopy(arg_dict)

    keys_to_remove = ['state', 'port']
    
    keys_in_dict = list(narg_dict.keys())
    
    for key in keys_in_dict:
        if key in keys_to_remove:
            del narg_dict[key]
    keys_required_for_payload = {}
    for mod in modify:
        command_to_run = ''
        cmd = cmd_templates[action][mod]
        
        command_to_run = ''
        
        command_template = Template(cmd)
        command = eval(command_template.substitute(**narg_dict))
        
        mod_to_check = ['show', 'enable', 'disable', 'del', 'rename', 'undel', 'assign', 'unassign', 'create']
        
        if mod not in mod_to_check:
            for key, value in config_to_modify[mod].items():
                payload[key] = value
                

        for arg in command:
            command_to_run = command_to_run + " " + str(arg)
        if command_to_run not in commands:
            command_to_run = command_to_run.replace('[', '').replace("'", '').replace(']', '').strip()
            commands[mod] = command_to_run
    payload = json.dumps(payload)
    return commands, payload


def check_if_object_present_absent(server, user, password, obj_key=None, command=None, endpoint=None, failed_cmd_out=None, headers=None, rename_keys=None, search_obj=None):
    port = 22
    if command is not None:
        cmd_output = dd_connect.dd_ssh(server, user, port, command, private_key=None, password=password, header=headers)
        jsonout = tab_to_json(cmd_output['output'], header=headers)
        status_code = True
        if not cmd_output['failed']:
            for fcode in failed_cmd_out:
                if fcode in str(cmd_output['output']):
                    status_code = False
                    break
            if status_code:
                if search_obj is not None and obj_key is not None:
                    num_obj = 0
                    if obj_key == 'user':
                        output = []
                        for obj in jsonout:
                            if obj['user'] in search_obj:
                                output.append(obj)
                        jsonout = output    
                        num_obj = len(search_obj)
                    else:
                        for obj in jsonout:
                            if obj[obj_key] == search_obj:
                                jsonout = [obj]
                                break
                        num_obj = 1
                if len(jsonout) != num_obj:
                    return [False, jsonout]
                else:
                    return [True, jsonout]
            else:
                return [False, jsonout]
        else:
            return [False, jsonout]
        
    elif endpoint is not None:
        cmd_output = dd_connect.dd_requests(server, user, api_pass=password, endpoint=endpoint, request_type='get', payload=None, query_params=None, field_params=None)
        if not cmd_output['failed']:
            return [True,  cmd_output['output']]
        else:
            return [False,  cmd_output['output']]


def check_if_modify_required(arg_dict, obj_key, obj_config):
    modify = []
    config_to_modify = {}
    keys_to_remove = ['state', 'port']
    temp_req_config = {}

    temp_req_config = copy.deepcopy(arg_dict)
    for key in arg_dict:
        if key in keys_to_remove:
            if key in temp_req_config:
                del temp_req_config[key]
    
    if arg_dict['state'] == 'present':
        if obj_key == 'storage_unit':
            storage_units = [ sub['storage_unit'] for sub in obj_config ]
            if arg_dict['storage_unit'] in storage_units:
                if 'new_storage_unit' in temp_req_config:
                    if 'rename' not in modify:
                        modify.append('rename')
                else:
                    for obj in obj_config:
                        if obj['storage_unit'] == arg_dict['storage_unit']:
                            obj_config = obj
                            break
                    
                    if 'user' in temp_req_config:
                        if temp_req_config['user'][0] == obj_config['user']:
                            config_to_modify = obj_config
                            if obj_config['status'] == 'D':
                                if 'undel' not in modify:
                                    modify.append('undel')
                                if 'undel' not in config_to_modify:
                                    config_to_modify['undel'] = {}
                        else:
                            if obj_config['status'] == 'D':
                                if 'undel' not in modify:
                                    modify.append('undel')
                                if 'undel' not in config_to_modify:
                                    config_to_modify['undel'] = {}
                            if 'modify' not in modify:
                                modify.append('modify')
                            if 'modify' not in config_to_modify:
                                config_to_modify['modify'] = {}
                            config_to_modify['modify']['user'] = temp_req_config['user'][0]
                            

                        
                    else:
                        if obj_config['status'] == 'D':
                            if 'undel' not in modify:
                                modify.append('undel')
                            if 'undel' not in config_to_modify:
                                config_to_modify['undel'] = {}
                        
            else:
                if 'new_storage_unit' in temp_req_config:
                    pass

            #     if 'create' not in modify:
            #         modify.append('create')
            #     if 'create' not in config_to_modify:
            #         config_to_modify['create'] = {}
            #     config_to_modify = arg_dict
        elif obj_key == 'user':
            user_list = [ sub['user'] for sub in obj_config ]
            for user in temp_req_config['user']:
                if user not in user_list:
                    if 'assign' not in modify:
                        modify.append('assign')
                    if 'assign' not in config_to_modify:
                        config_to_modify['assign'] = {}
                    
                    if 'user' not in config_to_modify['assign']:
                        config_to_modify['assign']['user'] = []
                    config_to_modify['assign']['user'].append(user)
        else:
            if 'enabled' in str(obj_config):
                pass
            else:
                if 'enable' not in modify:
                    modify.append('enable')
                if 'enable' in config_to_modify:
                    config_to_modify['enable'] = {}
        
    else:
        if obj_key == 'storage_unit':
            storage_units = [ sub['storage_unit'] for sub in obj_config ]
            if arg_dict['storage_unit'] in storage_units:
                for obj in obj_config:
                    if obj['storage_unit'] == arg_dict['storage_unit']:
                        obj_config = obj
                        break
                if obj_config['status'] != 'D':
                    if 'del' not in modify:
                        modify.append('del')
                    if 'del' not in config_to_modify:
                        config_to_modify['del'] = {}
                    config_to_modify['del']['storage_unit'] = temp_req_config['storage_unit']
                else:
                    config_to_modify = obj_config
        elif obj_key == 'user':
            user_list = [ sub['user'] for sub in obj_config ]
            for user in temp_req_config['user']:
                if user not in user_list:
                    pass
                else:
                    if 'unassign' not in modify:
                        modify.append('unassign')
                    if 'unassign' not in config_to_modify:
                        config_to_modify['unassign'] = {}
                    if 'user' not in config_to_modify['unassign']:
                        config_to_modify['unassign']['user'] = []
                    config_to_modify['unassign']['user'].append(user)
        else:
            if 'disable' in str(obj_config):
                pass
            else:
                if 'disable' not in modify:
                    modify.append('disable')
                if 'disable' not in config_to_modify:
                    config_to_modify['disable'] = {}
    return modify, config_to_modify 


def change_object(server, user, password, command=None, endpoint=None, request_type=None, payload=None):
    port = 22
    if command is not None:
        cmd_output = dd_connect.dd_ssh(server, user, port, command, private_key=None, password=password, header=None)
        # jsonout = nfs_output(output=cmd_output['output'])
        if not cmd_output['failed']:
            return [True, cmd_output['output']]
        else:
            return [False, cmd_output['output']]
    elif endpoint is not None:
      cmd_output = dd_connect.dd_requests(server, user, api_pass=password, endpoint=endpoint, request_type=request_type, payload=payload, query_params=None, field_params=None)
      if not cmd_output['failed']:
          return [True,  cmd_output['output']]
      else:
          return [False,  cmd_output['output']]


def main():
    fields = {
    'state': {'type': 'str', 'choices': ['present', 'absent'], 'required': True},
    'storage_unit': {'type': 'str', 'required': False},
    'tenant-unit': {'type': 'str', 'required': False},
    'new_storage_unit': {'type': 'str', 'required': False},
    'user': {'type': 'list', 'required': False},
    'skip-chown': {'type': 'bool', 'required': False},
    'host': {'type': 'str', 'required': True},
    'port': {'type': 'int', 'default': 22},
    'username': {'type': 'str', 'required': True},
    'private_key': {'type': 'str', 'no_log': True},
    'password': {'type': 'str', 'no_log': True},
    }
    module = AnsibleModule(argument_spec=fields)
  
    server = module.params['host']
    user = module.params['username']
    port = module.params['port']
    password = module.params['password']
    meta_output = []
    arg_dict = {}
    for key, value in module.params.items():
        if isinstance(value, dict):
            if key not in arg_dict:
                arg_dict[key] = {}
            for kv, v in value.items():
                if v is not None:
                    arg_dict[key][kv] = v
        else:
            if value is not None:
                arg_dict[key] = value
    keys_to_delete = ['host', 'username', 'private_key', 'password']
    
    for key in keys_to_delete:
        if key in arg_dict:
            del arg_dict[key]

    cmd_output = {}
    conditions, cmd_templates, headers, rename_keys = ddboost()
    failed_cmd_out = ['does not exist']
    obj_keys = []
    obj_key = get_obj_key(arg_dict, obj_keys)

    action = condition_check(conditions, command_build_dict=arg_dict)
    if action == 'storage_unit' or action == 'user':
        search_obj = arg_dict[action]
    else:
        search_obj = None
    modify = ['show']
    if len(action) > 0:
        commands, payload = build_commands(modify, action, arg_dict, obj_key, cmd_templates, config_to_modify={})
        if len(commands) > 0:
            
            obj_exists, obj_config = check_if_object_present_absent(server, user, password, obj_key=action, command=commands[modify[0]], endpoint=None, failed_cmd_out=failed_cmd_out, headers=headers[action], rename_keys=None, search_obj=search_obj)
            cmd_output['output'] = obj_config
            cmd_output['changed'] = False
            cmd_output['failed'] = False
            if obj_exists:
                modify, config_to_modify = check_if_modify_required(arg_dict, obj_key=action, obj_config=obj_config)

                if len(modify) > 0:
                    commands, payload = build_commands(modify, action, arg_dict, obj_key=action, cmd_templates=cmd_templates, config_to_modify=config_to_modify)
                    if len(commands) > 0:
                        status = []
                        output = []
                        for key in commands:
                            command = commands[key]
                            if command.startswith('/'):
                                sts, opt = change_object(server, user, password, command=None, endpoint=command, request_type='put', payload=payload)
                            else:
                                sts, opt = change_object(server, user, password, command=command, endpoint=None, request_type=None, payload=None)
                            status.append(sts)
                            output.append(opt)
                        if all(status):
                            changed = True
                            failed = False
                        else:
                            changed = False
                            failed = True

                        cmd_output['output'] = output
                        cmd_output['changed'] = changed
                        cmd_output['failed'] = failed
                    else:
                        cmd_output['output'] = obj_config
                        cmd_output['changed'] = False
                        cmd_output['failed'] = False
                else:
                    cmd_output['output'] = obj_config
                    cmd_output['changed'] = False
                    cmd_output['failed'] = False   
            else:
                if arg_dict['state'] == 'present':
                    config_to_modify = copy.deepcopy(arg_dict)
                    keys_to_remove = ['state', 'port']
                    for key in keys_to_remove:
                        if key in config_to_modify:
                            del config_to_modify[key]
                    
                    if action == 'storage_unit':
                        if 'new_storage_unit' not in arg_dict:
                            modify = ['create']
                            commands, payload = build_commands(modify, action, arg_dict, obj_key=action, cmd_templates=cmd_templates, config_to_modify=config_to_modify)
                            if len(commands) > 0:
                                status = False
                                for key in commands:
                                    command = commands[key]
                                    status, output = change_object(server, user, password, command=command, endpoint=None, request_type=None, payload=None)
                                if status:
                                    changed = True
                                    failed = False
                                else:
                                    changed = False
                                    failed = True

                                cmd_output['output'] = output
                                cmd_output['changed'] = changed
                                cmd_output['failed'] = failed
                        else:
                            cmd_output['output'] = f"Storage unit {arg_dict['storage_unit']} does not exists or already renamed to {arg_dict['new_storage_unit']}"
                            cmd_output['changed'] = False
                            cmd_output['failed'] = False
                    else:
                        modify = ['assign'] 
                        commands, payload = build_commands(modify, action, arg_dict, obj_key=action, cmd_templates=cmd_templates, config_to_modify=config_to_modify)
                        if len(commands) > 0:
                            status = False
                            for key in commands:
                                command = commands[key]
                                status, output = change_object(server, user, password, command=command, endpoint=None, request_type=None, payload=None)
                            if status:
                                changed = True
                                failed = False
                            else:
                                changed = False
                                failed = True

                            cmd_output['output'] = output
                            cmd_output['changed'] = changed
                            cmd_output['failed'] = failed
                                  

    else:
        cmd_output['output'] = 'Please check the input parameters and rerun the playbook.'
        cmd_output['failed'] = False
        cmd_output['changed'] = False            

    module.exit_json(failed=cmd_output['failed'], msg=cmd_output['output'], changed=cmd_output['changed'])


if __name__ == '__main__':
    main()