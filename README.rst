==============
handbrakecloud
==============

Overview
--------

handbrakecloud is a daemon for managing transcoding videos dynamically on an
OpenStack cloud using HandBrake. It leverages Ansible to manage both OpenStack
resources as well as setting the local environment in each server it launches.

handbrakecloud will watch a directory for yaml job files which contain an input
and output path, as well as any options for transcoding the video. (a REST API,
or socket interface may be added in the future to augment the directory
watching) handbrakecloud will then launch a server (if necessary) and setup
the environment on the server so that Handbrake is installed. Once the
environment is ready it will launch handbrake to transcode the file. After it
is done the server will be returned to a pool for future use. (note servers
are currently never deleted, this is a future todo)

Installing handbrakecloud
-------------------------

To install handbrake cloud you first need to locally clone the repo with::

  git clone https://github.com/mtreinish/handbrakecloud.git

Then you can install by running::

  pip install -U handbrakecloud

Which will install handbrake cloud into your python environment. (it might need
root privleges depending on your system)

You can also install it for development with::

  pip install -e handbrakecloud

which will install handbrakecloud in your python environment in editable mode for
local development

Running handbrakecloud
----------------------

Running handbrakecloud is fairly straightforward (the real work is in
configuration) you just run the handbrakecloud command with a single argument
the path to the config file. For example::

    handbrakecloud config.yaml

Configuring handbrakecloud
--------------------------

All the configuration (and job files) are done in yaml. To create a
configuration you need to provide some basic information on how handbrakecloud
will operate. Here is an example of the mandatory minimum settings needed in
the config file::

    job_file_dir: /tmp/jobs
    cloud:
      flavor: 3
      key_name: openstack_key
      image_name: ubuntu
      remote_user: ubuntu

``job_file_dir`` tells handbrake cloud the directory to watch for job files
being added. The ``cloud`` field tells handbrake how to use the OpenStack cloud
to create and use resources when it needs to. ``flavor`` is the flavor id of
the flavor to use when booting servers, ``key_name`` is the keypair name on
the cloud to use on the server, ``image_name`` is the name of the image to use
while booting, and ``remote_user`` is the username handbrake cloud should use
when it needs to ssh into the server after it's booted.

There are also several optional settings you can provide to tweak how
handbrakecloud will operate. For example a full config file would look like::

    job_file_dir: /tmp/jobs
    profile:
      audio:
        encoder: copy
      video:
        encoder: x264
        quality: 20
    max_workers: 10
    worker_name_prefix: handbrake
    job_poll_interval: 50
    cloud:
      flavor: 3
      key_name: openstack_key
      image_name: ubuntu
      remote_user: ubuntu
    log_path: handbrakecloud.log
    deploy_playbook_path: /etc/handbrakecloud/deploy_worker_mycloud.yaml
    run_playbook_path: /etc/handbrakecloud/run_handbrake_mycloud.yaml
    retry_on_fail: True

``max_workers`` is the max number of servers handbrakecloud can create. By
default this is set to 0 which means no maximum. ``worker_name_prefix`` is the
prefix to use in the created server names. By default this is set to
*handbrakecloud-worker*. ``job_poll_interval`` is the interval at which the
handbrakecloud daemon will poll the job_file_dir for new files being added. (in
seconds) By default it is set to 10 seconds. ``log_path`` is pretty self
explanatory and just specifies where you write the log file.

There are 2 options, ``deploy_playbook_path`` and ``run_playbook_path`` that
are used to specify alternative playbooks to use instead of the ones packaged
with handbrake cloud, which are the defaults if these options aren't
specified. The playbooks packaged with the project are very specific to my
working environment for trascoding (including things like mouting a nfsv4 share
that contains the files, using the private v4 ip for ssh, etc.). See the section
below on writing custom playbooks for more details.

The ``retry_on_fail`` parameter is used to tell handbrake cloud to retry a job
if the execution of handbrake fails for any reason. This is useful if the cloud
nodes are unreliable (either because of networking, or some other reason)
because the job will just be resubmitted. However, if there is a reason why
the transcode won't work, like corrupt source or a job misconfiguration, then
the bad job will never be flushed and stuck in a infinite loop of retries.

The ``profile`` section will be covered in more detail job files section
below, but at a high level this is used to specify global handbrake settings to
use by default when running transcoding jobs. They can be overridden on a case
by case basis inside a local job file. The concept is to set sane defaults for
you use case.

OpenStack Credentials and Auth Configuration
''''''''''''''''''''''''''''''''''''''''''''
For OpenStack credentials since handbrakecloud uses Ansible to do the resource
creation (which in turn uses `shade`_) you'll need to either specify your
credentials via a clouds.yaml file or the OS_* environment variables. You can
see more details of that in the `os-client-config documentation`_ (which is what
shade leverages for this). This is done completely outside of handbrakecloud,
and if you already have an openstack client configured in your environemnt
everything should just work in handbrakecloud.

.. _shade: https://docs.openstack.org/developer/shade/

Here are some examples of how you can configure OpenStack credentials. To use
environment variables, just make sure the appropriate OS_* variables set::

    OS_PROJECT_DOMAIN_NAME=Default
    OS_USER_DOMAIN_NAME=Default
    OS_PROJECT_NAME=project_foo
    OS_USERNAME=demo
    OS_PASSWORD=IAmARealPASSWORD123
    OS_AUTH_URL=http://openstack_cloud.domain:5000/v3
    OS_IDENTITY_API_VERSION=3

Or you can also create a clouds.yaml file which will contain all of these
settings. This file can live in the current Directory, ~/.config/openstack,
or /etc/openstack. An example of this file (from the `os-client-config documentation`_)
is::

    clouds:
      mtvexx:
        profile: vexxhost
        auth:
          username: mordred@inaugust.com
          password: XXXXXXXXX
          project_name: mordred@inaugust.com
        region_name: ca-ymq-1
        dns_api_version: 1
      mordred:
        region_name: RegionOne
        auth:
          username: 'mordred'
          password: XXXXXXX
          project_name: 'shade'
          auth_url: 'https://montytaylor-sjc.openstack.blueboxgrid.com:5001/v2.0'
      infra:
        profile: rackspace
        auth:
          username: openstackci
          password: XXXXXXXX
          project_id: 610275
        regions:
        - DFW
        - ORD
        - IAD

.. _os-client-config documentation: https://docs.openstack.org/developer/os-client-config/

As you can see a clouds.yaml file lets you specify multiple clouds at once. If
your file has more than one cloud make sure you set the ``OS_CLOUD`` environment
variable so handbrakecloud knows which one to use.

Job Files
=========

Job files are the lifeblood of handbrakecloud and are used to tell handbrake
cloud how to run a transcode. When these are put in the configured jobs
directory they will launch a transcoding job. The basic file format for these
is::

    - source: /tmp/video_in.mkv
      output: /tmp/video_out.mkv
      chapters: true
      profile:
      audio:
        tracks:
          - 2
          - 5
      video:
        encoder_preset: film

Note that a job file can define an arbitrary number of jobs. handbrakecloud
will handle each invidual job separately. An example with 2 jobs is::

    - source: /tmp/video_in1.mkv
      output: /tmp/video_out1.mkv
      chapters: true
      profile:
      audio:
        tracks:
          - 2
          - 5
      video:
        encoder_preset: film
    - source: /tmp/video_in2.mkv
      output: /tmp/video_out2.mkv
      chapters: true
      profile:
      audio:
        tracks:
          - 2
          - 5
      video:
        encoder_preset: film

Profiles
--------

Profiles are specific encoder settings that are used to configure Handbrake
to run as you want. Anything in this section can be specified globally or
locally. A local setting will always take preference over a globally set one.
Right now the a full profile looks like::

    audio:
        encoder: copy,
        tracks:
          - 2
          - 3
    video:
        encoder: x264,
        encoder_preset: film
        quality: 20
    subtitle:
        tracks:
          - 1
          - 2
    filters:
        decomb: true

This will likely be expanded in the future, because it provides very limited
coverage of Handbrake's options.

Writing Custom Playbooks
------------------------

The packaged Ansible playbooks for both deploying a worker node and running
handbrake are very specific to my local cloud environment and if used outside
of that in all likelihood they will not work. However, they can serve as general
guide for creating your own custom playbooks for your own environment. In the
future the packaged playbooks might be changed to be more general purpose (at
the expense of more required configuration) but for right now the only option
is to write your own playbooks.

Deploy Node Playbook
--------------------
For the deploy node playbook this is likely where the most customization will
be needed, because everyone's environment will be different. The packaged
playbook gives an example of the basic steps you'll need to test which are:

 #. Create the server
 #. Set up the storage environment to access input and store output
 #. Install any required software and HandBrakeCLI (HandBrakeCLI must be
    installed)

In most situations the openstack pieces in the packaged playbooks should work
the same and can probably be reused, although the ip used for
``ansible_ssh_host`` may need to be changed depending on the network
configuration. The packaged playbook uses the private v4 address, but if your
cloud provides ssh on another interface you'll need to update that field. If
you need to create your own handbrakecloud will pass in the follow variable
which are required for booting a server on OpenStack:

 #. ``worker_name``: the server name to use
 #. ``image``: the image name to use for booting the server
 #. ``flavor_id``: the flavor_id to use for booting the server
 #. ``key_name``: the ssh key to use for the server

Related to that but not specifically about booting the server is the ``user``
variable which will be the ``ansible_user`` for the host which is the username
to use for sshing into the guest. (which is provided in the configuration file)

Once you have the server booted and added to the Ansible dynamic inventory you
can then run whatever tasks you need to setup the environment for steps #2 and
#3. The assumption handbrakecloud makes about the worker node after running the
playbook is that it will be able to call HandBrakeCLI on that node with any of
the options specified in the jobs submitted. (which includes input and output
directories)


Run Handbrake Playbook
----------------------

The run node playbook should remain mostly unchanged. handbrakecloud will
generate a command and pass that directly to the playbook for running, via the
``command`` variable. The packaged playbook handles this part fine, and it
probably shouldn't need to be changed at all. What likely will need to be
customized for this is the host/ip information to make sure that ansible ssh's
into the correct server. The ``worker_name`` variable will be used to pass the
server name into the playbook. You'll need to make sure your playbook will be
able to take that name and use it to ssh into the server, which depends on both
your OpenStack environment as well as your local ansible configuration.
