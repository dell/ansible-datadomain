# Copyright ©️ 2022 Dell Inc. or its subsidiaries.
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase


class ActionModule(ActionBase):
    TRANSFERS_FILES = False

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        # command = module_return['command']
        if self._task.environment and any(self._task.environment):
            self._display.warning('raw module does not support the environment keyword')

        result = super(ActionModule, self).run(tmp, task_vars)
        # del tmp  # tmp no longer has any effect
        params = self._task.args
        params['host'] = str(task_vars['inventory_hostname'])
        params['port'] = str(task_vars['ansible_port'])
        params['username'] = str(task_vars['ansible_user'])

        if 'private_key_file' in task_vars:
            params['private_key'] = str(task_vars.get('private_key_file', False))
        if 'ansible_ssh_pass' in task_vars:
            params['password'] = task_vars.get('ansible_ssh_pass', False)

        module_name = "dellemc.datadomain.replication"
        if self._play_context.check_mode:
            # in --check mode, always skip this module execution
            result['skipped'] = True
            return result

        module_return = self._execute_module(module_name=module_name,
                                             module_args=params,
                                             task_vars=task_vars, tmp=tmp)
        if not module_return.get('failed'):
            result['msg'] = module_return['msg']
            result['changed'] = module_return['changed']
            result['failed'] = module_return['failed']
        else:
            result['msg'] = module_return
            result['failed'] = module_return['failed']
            result['changed'] = False
        return result
