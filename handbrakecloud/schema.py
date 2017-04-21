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

import voluptuous as vol


profile_schema = vol.Schema({
    'audio': {
        'encoder': str,
        'tracks': [int],
    },
    'video': {
        'encoder': str,
        'encoder_preset': str,
        'quality': int,
    },
    'subtitle': {
        'tracks': [int],
    },
    'filters': {
        str: bool,
    },
})


job_schema = vol.Schema([{
    vol.Required('source'): vol.PathExists,
    vol.Required('output'): vol.PathExists,
    vol.Optional('profile'): profile_schema,
    vol.Optional('chapters'): bool,
    vol.Optional('title'): int,
}])

global_config = vol.Schema({
    vol.Required('job_file_dir'): vol.PathExists,
    vol.Optional('profile'): profile_schema,
    vol.Optional('max_workers'): int,
    vol.Optional('worker_timeout'): int,
    vol.Required('cloud'): {
        'flavor': int,
        'key_name': str,
        'image_name': str,
        'remote_user': str,
    },
    vol.Optional('worker_name_prefix'): str,
    vol.Optional('log_path'): vol.PathExists,
    vol.Optional('job_poll_interval'): int,
})
