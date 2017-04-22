# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import subprocess

from ansible.executor import playbook_executor
from ansible import inventory as ansible_inv
from ansible.parsing import dataloader
from ansible import vars as variables
from collections import namedtuple

from handbrakecloud import exceptions

LOG = logging.getLogger(__name__)


OPTIONS = namedtuple('Options',
                     ['listtags', 'listtasks', 'listhosts', 'syntax',
                      'connection', 'module_path', 'forks', 'remote_user',
                      'private_key_file', 'ssh_common_args', 'ssh_extra_args',
                      'sftp_extra_args', 'scp_extra_args', 'become',
                      'become_method', 'become_user', 'verbosity', 'check'])


def run_playbook(playbook, extra_vars):
    options = OPTIONS(listtags=False, listtasks=False, listhosts=False,
                      syntax=False, connection='ssh', module_path=None,
                      forks=100, remote_user='ubuntu', private_key_file=None,
                      ssh_common_args=None, ssh_extra_args=None,
                      sftp_extra_args=None, scp_extra_args=None, become=True,
                      become_method=None, become_user='root', verbosity=3,
                      check=False)

    variable_manager = variables.VariableManager()
    variable_manager.extra_vars = extra_vars
    loader = dataloader.DataLoader()
    inventory = ansible_inv.Inventory(loader=loader,
                                      variable_manager=variable_manager,
                                      host_list='localhost')
    variable_manager.set_inventory(inventory)
    executor = playbook_executor.PlaybookExecutor(
        playbooks=[playbook],
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        options=options,
        passwords=None)
    executor.run()


def handle_error(stdout, stderr, return_code):
    instance_error_msg = '"msg": "Error in creating instance'
    if instance_error_msg in stdout:
        raise exceptions.InstanceCreateException()


# Only using this until I can figure out the ansible python API
def run_playbook_subprocess(playbook, extra_vars):
    extra_vars_string = ""
    for var in extra_vars:
        extra_vars_string += "%s='%s' " % (var, extra_vars[var])
    extra_vars_string = extra_vars_string.rstrip()
    cmd = ['ansible-playbook', playbook, '--extra-vars', extra_vars_string]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if proc.returncode > 0:
        handle_error(stdout, stderr, proc.returncode)
        LOG.error("Playbook %s failed with:\n\tstderr:\n\t\t%s"
                  "\n\tstdout:\n\t\t%s" % (playbook, stderr, stdout))
        raise exceptions.PlaybookFailure
