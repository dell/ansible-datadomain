# Copyright ©️ 2022 Dell Inc. or its subsidiaries.
from string import Template
from . import dd_connect
import json


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
    return action, check_status_ep


def build_command(action, arg_dict, supported_commands, conditions):
    argument_dict = {}
    will_change = conditions[action]['will_change']
    header = conditions[action]['header']
    is_filter = None
    for key, value in arg_dict.items():
        key = key.replace("-", "_")
        argument_dict[key] = value

    command_template = Template(supported_commands[action])

    command = eval(command_template.substitute(**argument_dict))

    if isinstance(eval(supported_commands[action]), list):
        if 'opt_key' in conditions[action]:
            opt_keys = conditions[action]['opt_key']
            for opt_key in opt_keys:
                if opt_key in arg_dict:
                    if not isinstance(arg_dict[opt_key], dict):
                        attr = f'{opt_key} {arg_dict[opt_key]}'
                        command.append(attr)
                    else:
                        for key, value in arg_dict[opt_key].items():

                            if value is not None:
                                attr = f'{key} {value}'

                                command.append(attr)
    else:
        if 'opt_key' in conditions[action]:
            opt_keys = conditions[action]['opt_key']
            for opt_key in opt_keys:
                if opt_key in argument_dict:
                    for key, value in arg_dict[opt_key].items():
                        key = key.replace("-", "_")
                        if value is not None:
                            command[key] = value
        if 'is_filter' in conditions[action]:
            filter = conditions[action]['is_filter']
            is_filter = arg_dict[filter]
        else:
            is_filter = None
    return command, will_change, is_filter, header


def run_cmd(module, command, is_filter, server, user, port, private_key=None, password=None, header=None):
    cmd_output = []
    cmd_out = {}

    if isinstance(command, list):
        cmd = " ".join(
            str(command).replace("[", "").replace("]", "").replace("'", "").replace(":", "").replace("{", "").replace(
                "}", "").replace('"', '').split(", "))
        if 'repl-port' in cmd:
            cmd = cmd.replace('repl-port', 'port')
        else:
            cmd = cmd
        cmd_output = dd_connect.dd_ssh(server, user, port, cmd, private_key, password, header)
    else:
        cmd = json.dumps(command)
        if is_filter is None and module.params['state'] == 'add':
            cmd_output = dd_connect.dd_requests(server, user, api_pass=module.params['dd-password'], is_filter=is_filter,
                                                version='v1.0', module='users', request_type='post', payload=cmd)

        elif is_filter is not None and module.params['state'] == 'change':
            cmd_output = dd_connect.dd_requests(server, user, api_pass=module.params['dd-password'], is_filter=is_filter,
                                                version='v1.0', module='users', request_type='put', payload=cmd)
        else:
            cmd_out['status'] = False
            cmd_out['output'] = 'Detected RestAPI call but No Condition matched to proceed'
            cmd_output.append(cmd_out)

    return cmd_output


