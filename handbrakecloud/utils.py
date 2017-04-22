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


def get_profile_args(global_profile, local_profile):
    args = []
    a_encoder = None
    a_tracks = None
    # Audio Settings
    if 'audio' in global_profile:
        if 'encoder' in global_profile['audio']:
            a_encoder = global_profile['audio']['encoder']
        if 'tracks' in global_profile['audio']:
            a_tracks = ','.join(
                [str(x) for x in global_profile['audio']['tracks']])
    if 'audio' in local_profile:
        if 'encoder' in local_profile['audio']:
            a_encoder = local_profile['audio']['encoder']
        if 'tracks' in local_profile['audio']:
            a_tracks = ','.join(
                [str(x) for x in local_profile['audio']['tracks']])
    if a_encoder:
        args.extend(['-E', a_encoder])
    if a_tracks:
        args.extend(['-a', a_tracks])
    # Video Settings
    v_encoder = None
    v_encoder_preset = None
    v_quality = None
    if 'video' in global_profile:
        if 'encoder' in global_profile['video']:
            v_encoder = global_profile['video']['encoder']
        if 'quality' in global_profile['video']:
            v_quality = global_profile['video']['quality']
        if 'encoder_preset' in global_profile['video']:
            v_encoder_preset = global_profile['video']['encoder_preset']
    if 'video' in local_profile:
        if 'encoder' in local_profile['video']:
            v_encoder = local_profile['video']['encoder']
        if 'quality' in local_profile['video']:
            v_quality = local_profile['video']['quality']
        if 'encoder_preset' in local_profile['video']:
            v_encoder_preset = local_profile['video']['encoder_preset']
    if v_encoder:
        args.extend(['-e', v_encoder])
    if v_quality:
        args.extend(['-q', str(v_quality)])
    if v_encoder_preset:
        args.extend(['--encoder-tune', v_encoder_preset])
    # Subtitle Settings
    s_tracks = None
    if 'subtitle' in global_profile:
        if 'tracks' in global_profile['subtitle']:
            s_tracks = ','.join(
                [str(x) for x in global_profile['subtitle']['tracks']])
    if 'subtitle' in local_profile:
        if 'tracks' in local_profile['subtitle']:
            s_tracks = ','.join(
                [str(x) for x in local_profile['subtitle']['tracks']])
    if s_tracks:
        args.extend(['-s', s_tracks])
    # Filter Settings
    decomb_filter = False
    if 'filters' in global_profile:
        if 'decomb' in global_profile['filters']:
            if global_profile['filters']['decomb']:
                decomb_filter = True
    if 'filters' in local_profile:
        if 'decomb' in local_profile['filters']:
            if local_profile['filters']['decomb']:
                decomb_filter = True
    if decomb_filter:
        args.append('-5')
    return args


def generate_command(jobs, global_config):
    job = jobs[0]
    input_file = job['source']
    output_file = job['output']
    command = ['HandBrakeCLI', '-i', input_file, '-o', output_file]
    if 'title' in job:
        command.append('-t')
        command.append(str(job['title']))
    else:
        command.append('--main-feature')
    if job.get('chapters'):
        command.append('-m')
    command.extend(get_profile_args(global_config.get('profile', {}),
                                    job.get('profile', {})))
    return ' '.join(command)
