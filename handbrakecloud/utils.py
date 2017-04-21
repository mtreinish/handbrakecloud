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

def generate_command(job, global_config):
    input_file = job['source']
    output_file = job['output']
    command = ['HandBrakeCLI', '-i', input_file, '-o', output_file]
    if 'title' in job:
        command.append('-t')
        command.append(job['title'])
    else
        command.append('--main-feature')
    if job.get('chapters'):
        command.append('m')
