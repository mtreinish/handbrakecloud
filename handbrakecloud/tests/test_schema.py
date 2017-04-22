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

from handbrakecloud import schema
from handbrakecloud.tests import base


class TestSchema(base.TestCase):
    def test_job_schema(self):
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
        schema.job_schema(job)
