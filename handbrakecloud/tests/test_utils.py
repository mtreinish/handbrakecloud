# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from handbrakecloud.tests import base
from handbrakecloud import utils

class TestUtils(base.TestCase):
    def test_get_profile_args_with_split_global_and_local(self):
        local_profile = {
            'audio': {
                'tracks': [2, 5]
            },
            'video': {
                'encoder_preset': 'film'
            }
        }
        global_profile = {
            'audio': {
                'encoder': 'copy'
            },
            'video': {
                'encoder': 'x264',
                'quality': 20,
            },
        }
        result = utils.get_profile_args(global_profile, local_profile)
        args = ['-E', 'copy', '-a', '2,5', '-e', 'x264', '-q', '20',
                '--encoder-tune', 'film']
        self.assertEqual(args, result)

    def test_generate_command(self):
        job = [{
            'profile': {
                'audio': {
                    'tracks': [2, 5]
                },
                'video': {
                    'encoder_preset': 'film'
                }
            },
            'source': '/tmp/input',
            'chapters': True,
            'output': '/tmp/output'
        }]
        global_config = {
            'job_file_dir': '/tmp/jobs',
            'profile': {
                'audio': {
                    'encoder': 'copy'
                },
                'video': {
                    'encoder': 'x264',
                    'quality': 20,
                },
            },
            'max_workers': 5,
            'worker_timeout': 600,
            'cloud': {
                'flavor': 3,
                'key_name': 'pub_key',
                'image_name': 'ubuntu',
                'remote_user': 'ubuntu',
            },
            'log_path': 'handbrakecloud.log',
        }
        result = utils.generate_command(job, global_config)
        command = ('HandBrakeCLI -i /tmp/input -o /tmp/output --main-feature '
                   '-m -E copy -a 2,5 -e x264 -q 20 --encoder-tune film')
        self.assertEqual(command, result)
