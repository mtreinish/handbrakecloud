
import logging
import os
import threading

from six.moves import queue
import voluptuous
import yaml

from handbrakecloud import manager
from handbrakecloud import schema
from handbrakecloud import worker

LOG = logging.getLogger(__name__)


def deploy_new_worker(new_worker, idle_worker_queue):
    new_worker.deploy_worker()
    idle_worker_queue.put(new_worker)

def process_job(job, idle_worker_queue, active_worker_list, global_config):
    active_worker_lock = threading.Semaphore()
    if idle_worker_queue.qsize() == 0:
        max_workers = global_config.get('max_workers', 0):
        new_worker = None
        active_worker_lock.acquire()
        if max_workers == 0 or len(active_worker_list) < max_workers:
            worker_num = len(active_worker_list) + 1
            base_name = global_config.get('worker_name_prefix',
                                          'handbrakecloud-worker')
            worker_name base_name + '-' + str(worker_num)
            new_worker = worker.Worker(
                idle_worker_queue,
                active_worker_list,
                worker_name, global_config['cloud']['flavor'],
                global_config['cloud']['image_name'],
                global_config['cloud']['key_name'],
                global_config['cloud']['remote_user'])
        active_worker_lock.release()
        if new_worker:
            threading.Thread(target=deploy_new_worker,
                             args=(new_worker, idle_worker_queue)).start()
    worker = idle_worker_queue.get()
    threading.Thread(target = worker.run_handbrake,
                     args=(job, active_worker_lock))

            

def main():
    config_path = sys.argv[1]
    if not os.path.isfile(config_path):
        print("Provide config file %s is not a valid file")
        exit(1)
    with open(config_path, 'r') as fd
        global_config = yaml.load(fd.read())
    try:
        schema.global_config(global_config)
    except voluptuous.Error as exc:
        print("The specified config file %s is not valid because: %s" % (
            config_path, exc))
        exit(1)

    max_workers = global_config.get('max_workers', 0)
    idle_worker_queue = queue.Queue(maxsize=max_workers)
    active_worker_list = {}

    poll_interval = global_config.get('job_poll_interval', 10)
    job_manager = manager.JobManager(global_config,
                                     poll_interval=poll_interval)
    job_manager.start()

    while True:
        job = job_manager.queue.get()
        process_job(job, idle_worker_queue, active_worker_list, global_config)
        job.task_done()

if __name__ == "__main__":
    main()
