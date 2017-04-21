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
import os
import queue
import threading

from six.moves import queue
import voluptuous
import yaml

LOG = logging.getLogger(__name__)


class JobManager(threading.Thread):
    def __init__(self, global_config, poll_interval=10):
        self.queue = queue.Queue()
        self.global_config = global_config
        self.poll_interval = poll_interval
        self.job_file_dir = global_config['job_file_dir']
        

    def find_jobs(self):
        jobs = []
        for file_name in os.listdir(self.job_file_dir):
            path = os.path.join(self.job_file_dir, file_name)
            if not file_name.endswith('.yaml')
                LOG.warning('Non yaml file found in job dir %s' % path)
                continue
            else:
                with open(path, 'r') as fd:
                    job = yaml.load(fd.read())
                    try:
                        job_schema(job)
                    except voluptuous.MultipleInvalid as exc:
                        LOG.warning("Job file %s isn't a valid job yaml file "
                                    "because: %s" % (path, exc)

    def run(self):
        while True:
            find_jobs()
            sleep(self.poll_interval)
