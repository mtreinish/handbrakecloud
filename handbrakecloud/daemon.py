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
import sys
import threading

from six.moves import queue
import voluptuous
import yaml

from handbrakecloud import manager
from handbrakecloud import schema
from handbrakecloud import worker

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

active_worker_lock = threading.Semaphore()
worker_builds = {}
worker_count_lock = threading.Semaphore()


def deploy_new_worker(new_worker, idle_worker_queue):
    try:
        new_worker.deploy_worker()
    except Exception:
        # If worker launch failed don't add it to the queue. The job
        # will just wait for the next idle node
        LOG.error('Worker: %s deploy failed' % new_worker.name)
        LOG.debug("deploy_new_worker() acquired the worker_count semaphore to "
                  "remove the failed deploy from the worker counts.")
        worker_count_lock.acquire()
        worker_builds.pop(new_worker.name)
        worker_count_lock.release()
        LOG.debug("deploy_new_worker() released the worker_count semaphore "
                  "after remove the failed deploy from the worker counts.")
        # Launch worker delete in spare thread to not block on failure
        threading.Thread(target=new_worker.delete_worker)
        return
    LOG.info("Launched new worker %s" % new_worker.name)
    idle_worker_queue.put(new_worker)


def process_job(job, idle_worker_queue, active_worker_list, global_config):
    LOG.info("Processing job with output file %s" % job.get('output'))
    if idle_worker_queue.qsize() == 0:
        max_workers = global_config.get('max_workers', 0)
        new_worker = None
        worker_count_lock.acquire()
        LOG.debug("process_job() acquired the worker_count semaphore to check "
                  "worker counts.")
        if max_workers == 0 or (len(worker_builds) < max_workers):
            worker_count = len(worker_builds)
            base_name = global_config.get('worker_name_prefix',
                                          'handbrakecloud-worker')
            worker_name = base_name + '-' + str(worker_count)
            # Handle failed deploys by incrementing the count until we find
            # an unused id
            if worker_name in worker_builds:
                while worker_name not in worker_builds:
                    worker_count += 1
                    base_name = global_config.get('worker_name_prefix',
                                                  'handbrakecloud-worker')
                    worker_name = base_name + '-' + str(worker_count)

            new_worker = worker.Worker(
                idle_worker_queue,
                active_worker_list,
                worker_name, global_config['cloud']['flavor'],
                global_config['cloud']['image_name'],
                global_config['cloud']['key_name'],
                global_config['cloud']['remote_user'],
                global_config)
            worker_builds[worker_name] = new_worker
        worker_count_lock.release()
        LOG.debug("process_job() released the active_list semaphore after "
                  "checking the active worker counts.")
        if new_worker:
            LOG.debug("Launching new worker: %s" % worker_name)
            deploy_new_worker(new_worker, idle_worker_queue)
        else:
            LOG.debug("Max number of active workers running already new jobs "
                      "are queued until a running worker is idle")
    active_worker = idle_worker_queue.get()
    active_worker_lock.acquire()
    LOG.debug("Worker: %s acquired active_list semaphore in "
              "run_handbrake() for marking itself active" % active_worker.name)
    if active_worker.name in active_worker_list:
        LOG.error("Duplicate name %s found in active worker list, something "
                  "went horribly wrong" % active_worker.name)
    active_worker_list[active_worker.name] = active_worker
    active_worker_lock.release()
    LOG.debug("Worker %s released semaphore active_list in "
              "run_handbrake() after marking itself "
              "active" % active_worker.name)
    start = datetime.datetime.utcnow()
    active_worker.run_handbrake(job, active_worker_lock)
    duration = datetime.datetime.utcnow() - start
    LOG.info('Finished transcoding job with output file %s in %s seconds'
             % (job.get('output'), duration.total_seconds()))


def main():
    config_path = sys.argv[1]
    if not os.path.isfile(config_path):
        print("Provide config file %s is not a valid file")
        exit(1)
    with open(config_path, 'r') as fd:
        global_config = yaml.load(fd.read())
    try:
        schema.global_config(global_config)
    except voluptuous.Error as exc:
        print("The specified config file %s is not valid because: %s" % (
            config_path, exc))
        exit(1)
    if 'log_path' not in global_config:
        LOG.addHandler(logging.StreamHandler())
    logging.basicConfig(filename=global_config.get('log_path'),
                        loglevel=logging.DEBUG)

    max_workers = global_config.get('max_workers', 0)
    idle_worker_queue = queue.Queue(maxsize=max_workers)
    active_worker_list = {}

    poll_interval = global_config.get('job_poll_interval', 10)
    job_manager = manager.JobManager(global_config,
                                     poll_interval=poll_interval)
    job_manager.start()

    while True:
        job = job_manager.queue.get()
        threading.Thread(target=process_job,
                         args=(job, idle_worker_queue, active_worker_list,
                               global_config)).start()
        job_manager.queue.task_done()

if __name__ == "__main__":
    main()
