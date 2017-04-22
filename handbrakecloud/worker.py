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

import datetime
import logging
import os

from handbrakecloud import runner
from handbrakecloud import utils

LOG = logging.getLogger(__name__)


def get_deploy_worker_playbook():
    file_path = os.path.abspath(__file__)
    playbooks_dir = os.path.join(os.path.dirname(file_path), 'playbooks')
    return os.path.join(playbooks_dir, 'deploy_node.yaml')


def get_run_handbrake_playbook():
    file_path = os.path.abspath(__file__)
    playbooks_dir = os.path.join(os.path.dirname(file_path), 'playbooks')
    return os.path.join(playbooks_dir, 'run_handbrake.yaml')


def get_delete_worker_playbook():
    file_path = os.path.abspath(__file__)
    playbooks_dir = os.path.join(os.path.dirname(file_path), 'playbooks')
    return os.path.join(playbooks_dir, 'delete_worker.yaml')


class Worker(object):
    def __init__(self, idle_queue, active_queue, name, flavor, image,
                 key_name, remote_user, global_config):
        self.idle_queue = idle_queue
        self.active_list = active_queue
        self.name = name
        self.flavor = flavor
        self.image = image
        self.key_name = key_name
        self.remote_user = remote_user
        self.start_time = None
        self.global_config = global_config

    def deploy_worker(self):
        extra_vars = {
            'worker_name': self.name,
            'flavor_id': self.flavor,
            'image': self.image,
            'key_name': self.key_name,
            'user': self.remote_user,
        }
        runner.run_playbook_subprocess(get_deploy_worker_playbook(),
                                       extra_vars=extra_vars)
        self.start_time = datetime.datetime.utcnow()

    def run_handbrake(self, job, worker_lock):
        command = utils.generate_command(job, self.global_config)
        extra_vars = {
            'command': command,
            'worker_name': self.name,
            'user': self.remote_user,
        }
        runner.run_playbook_subprocess(get_run_handbrake_playbook(),
                                       extra_vars=extra_vars)
        worker_lock.acquire()
        LOG.debug("Worker: %s acquired active_list semaphore in "
                  "run_handbrake() to mark itself as idle" % self.name)
        self.idle_queue.put(self.active_list.pop(self.name))
        worker_lock.release()
        LOG.debug("Worker: %s released active_list semaphore in "
                  "run_handbrake() after marking itself as idle" % self.name)
        self.start_time = datetime.datetime.utcnow()

    def get_idle_time(self):
        now = datetime.datetime.utcnow()
        delta = now - self.start_time
        return delta.total_seconds()

    def delete_worker(self):
        extra_vars = {
            'server': self.name,
        }
        runner.run_playbook_subprocess(playbook=get_delete_worker_playbook(),
                                       extra_vars=extra_vars)
