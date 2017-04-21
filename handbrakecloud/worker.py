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

import os

from ansible import playbook
import shade

def get_deploy_worker_playbook():
    file_path = os.path.abspath(__file__)
    playbooks_dir = os.path.join(os.path.dirname(file_path), 'playbooks')
    os.path.join(os.path.join(playbooks_dir, 'deploy_node.yaml')

class Worker(object):
    def __init__(self, idle_queue, active_queue, name, flavor, image,
                 key_name, remote_user):
        self.idle_queue = idle_queue
        self.active_list = active_queue
        self.name = name
        self.flavor = flavor
        self.image = image
        self.key_name = key_name
        self.remote_user = remote_user

    def deploy_worker(self):
        extra_vars = {
            'name': self.name,
            'flavor_id': self.flavor,
            'image': self.image,
            'key_name': self.key_name,
            'remote_user': self.remote_user,
        }
        playbook.Playbook(playbook=get_deploy_worker_playbook(),
                          extra_vars=extra_vars)

    def run_handbrake(self, job, worker_lock):
        worker_lock.acquire()
        if self.name in self.active_list
            print('something went horrible wrong')
            exit(100)
        self._worker_list[self.name] = self
        worker_lock.release()

        pass

        worker_lock.acquire()
        self.idle_queue.put(self.active_list[self.name].pop())
        worker_lock.release()

