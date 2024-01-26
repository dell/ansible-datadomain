# Copyright ©️ 2022 Dell Inc. or its subsidiaries.
import json
import os
import time
import urllib3
urllib3.disable_warnings()
import re

try:
    import paramiko
    import requests
    imported_modules = True
except ImportError as e:
    import_error = e
    imported_modules = False
#
# from ansible.parsing.dataloader import DataLoader
# from ansible.inventory.manager import InventoryManager

command_outout = {}
final_output = []


def dd_ssh(server, user, port, command, private_key=None, password=None, header=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if private_key is not None:
            k = paramiko.RSAKey.from_private_key_file(private_key)
            client.connect(hostname=server, username=user, pkey=k, port=port, banner_timeout=60)
        if password is not None:
            k = password
            client.connect(hostname=server, username=user, password=k, port=port, banner_timeout=60)
        stdin, stdout, stderr = client.exec_command(command)
        outerr = stderr.read().decode('utf-8')
        output = stdout.read().decode('utf-8')
        # output = tab_to_json(output=output, header=header)
        cmd_status = stdout.channel.recv_exit_status()
        if cmd_status == 0:
            command_outout['failed'] = False
            command_outout['output'] = output
        else:
            command_outout['failed'] = True
            command_outout['output'] = outerr
    except Exception as e:
        command_outout['failed'] = True
        command_outout['output'] = e
    return command_outout


def dd_requests(server, user, api_pass, endpoint, request_type, payload, query_params=None, field_params=None):
    try:
        url = f"https://{server}:3009/rest/v1.0/auth"

        headers = {'Content-Type': "application/json"
                                   }
        data = """\
                {"auth_info":{"username":"%s","password":"%s"}}\
                """ % (user, api_pass)
        # data = json.loads(data)
        r = requests.post(url, headers=headers, verify=False, auth=(user, api_pass), data=data)
        if 'X-DD-AUTH-TOKEN' in r.headers:
            dd_auth_token = r.headers['X-DD-AUTH-TOKEN']
        else:
            data = json.dumps({
                    "username": user,
                    "password": api_pass
                })

            r = requests.post(url, headers=headers, verify=False, data=data)
            if 'X-DD-AUTH-TOKEN' in r.headers:
                dd_auth_token = r.headers['X-DD-AUTH-TOKEN']
            # payload = json.dumps(payload)

        headers = {
            'X-DD-AUTH-TOKEN': dd_auth_token,
            'Content-Type': "application/json",
            'Accept': 'application/json'
        }

        if endpoint is None:
            url = f"https://{server}:3009{endpoint}"
        else:
            url = f"https://{server}:3009{endpoint}"
        if query_params is not None:
            # query_params = eval(query_params)
            if not isinstance(query_params, dict):
                raise TypeError("query_param should be a dictionary type. like {hostname: abc, level: Incr}")
            query_params = " and ".join(str(query_params).split(',')).replace("{", "").replace("}", "").replace("'", '')
            query_appender = 'filter=' + query_params
        if field_params is not None:
            # field_params = eval(field_params)
            if not isinstance(field_params, list):
                raise TypeError("query_param should be a list type. like [hostname,level]")
            fields = str(field_params).replace("[", "").replace("]", "").replace(", ", ",").replace("'",  "")
            field_appender = 'include_fields=' + fields
        if query_params is not None and field_params is not None:
            url = url + '?' + query_appender + '&' + field_appender
        elif query_params is not None and field_params is None:
            url = url + '?' + query_appender
        elif query_params is None and field_params is not None:
            url = url + '?' + field_appender
        else:
            url = url
        response = requests.request(f"{request_type}", url, headers=headers, verify=False, data=payload)
        success_service = [200, 201]
        if int(response.status_code) in success_service:
            command_outout['failed'] = False
            command_outout['output'] = eval(response.text)
        else:
            command_outout['failed'] = True
            command_outout['output'] = eval(response.text)
    except Exception as e:
        command_outout['failed'] = True
        command_outout['output'] = e

    return command_outout


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
