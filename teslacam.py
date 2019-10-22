# pylint: disable=line-too-long
' Tesla camera video post-processing module '
import argparse
import asyncio
import contextlib
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import timeit

import arg_parser
import time_duration

logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.INFO)
LOGGER = logging.getLogger('teslacam')
logging.getLogger('asyncio').setLevel(logging.INFO)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def get_video_stream_info(ffprobe_file_path, video_file_path):
    ' FFMPEG process to retrieve video metadata '
    ffprobe_cmd_line = [
        ffprobe_file_path,
        '-v', 'error',
        '-show_entries', 'stream=duration',
        '-print_format', 'json',
        '-i',
        video_file_path,
    ]
    LOGGER.info('gather video stream info from %s', video_file_path)
    proc = await asyncio.create_subprocess_exec(
        *ffprobe_cmd_line,
        stdout=asyncio.subprocess.PIPE
    )
    await proc.wait()
    LOGGER.info('completed gathering video stream info from %s', video_file_path)
    if proc.returncode:
        raise subprocess.CalledProcessError(
            proc.returncode,
            cmd=' '.join(ffprobe_cmd_line)
        )

    data = await proc.stdout.read()
    return json.loads(data)['streams'][0]


def get_longest_duration(existing_duration, new_duration):
    ' Decide how long a joined camera segment should play '
    float_existing_duration = float(existing_duration)
    float_new_duration = float(new_duration)
    if float_existing_duration >= float_new_duration:
        return existing_duration
    return new_duration


REGEX_VIDEO_FILENAME = re.compile(
    r'(\d\d\d\d-\d\d-\d\d_\d\d-\d\d-\d\d)-(\w+)\.mp4',
    re.IGNORECASE
)


async def populate_video_map(
    video_map,
    ffprobe_file_path,
    input_folder_path,
    video_filename
):
    ' Retrieve video metadata from raw video files '
    video_file_path = os.path.join(input_folder_path, video_filename)
    try:
        video_stream_info = await get_video_stream_info(
            ffprobe_file_path,
            video_file_path
        )
    except subprocess.CalledProcessError:
        LOGGER.warning('skip problematic video %s', video_file_path)
        return

    match_result = re.fullmatch(REGEX_VIDEO_FILENAME, video_filename)

    video_file_prefix = match_result.group(1)
    video_file_metadata = video_map.setdefault(video_file_prefix, {})

    video_file_camera_position = match_result.group(2)
    video_file_camera = video_file_metadata.setdefault('cameras', {})
    video_file_camera[video_file_camera_position] = video_file_path

    video_file_metadata['duration'] = get_longest_duration(
        video_file_metadata.setdefault('duration', '0'),
        video_stream_info['duration']
    )


async def create_video_file_map(
    ffprobe_file_path,
    input_folder_path,
    output_folder_path
):
    ' Enumerates video folder to find files to layout and concatenate '
    video_filenames = os.listdir(input_folder_path)

    video_map = {}
    await asyncio.gather(
        *(
            populate_video_map(
                video_map,
                ffprobe_file_path,
                input_folder_path,
                video_filename
            )
            for video_filename in video_filenames
        )
    )
    return video_map

def generate_layout_command_line(
    ffmpeg_file_path,
    codec,
    video_file_stream_info,
    layout_video_file_path
):
    ' FFMPEG command line that merges camera videos into one '
    stream_id = 0
    duration = video_file_stream_info['duration']
    ffmpeg_filter = f'color=duration={duration}:s=3840x1920:c=black [layer{stream_id}];'

    video_cameras = video_file_stream_info['cameras']
    video_camera_count = len(video_cameras.items())
    cmd_line = [ffmpeg_file_path]
    if 'left_repeater' in video_cameras:
        cmd_line += ['-i', video_cameras['left_repeater']]
        ffmpeg_filter += f'[{stream_id}:v]setpts=PTS-STARTPTS[left];'
        ffmpeg_filter += f'[layer{stream_id}][left]overlay=eof_action=pass:repeatlast=0:x=2560:y=960'
        stream_id += 1
        if video_camera_count > stream_id:
            ffmpeg_filter += f'[layer{stream_id}];'

    if 'front' in video_cameras:
        cmd_line += ['-i', video_cameras['front']]
        ffmpeg_filter += f'[{stream_id}:v]setpts=PTS-STARTPTS[front];'
        ffmpeg_filter += f'[layer{stream_id}][front]overlay=eof_action=pass:repeatlast=0:x=1280:y=0'
        stream_id += 1
        if video_camera_count > stream_id:
            ffmpeg_filter += f'[layer{stream_id}];'

    if 'right_repeater' in video_cameras:
        cmd_line += ['-i', video_cameras['right_repeater']]
        ffmpeg_filter += f'[{stream_id}:v]setpts=PTS-STARTPTS[right];'
        ffmpeg_filter += f'[layer{stream_id}][right]overlay=eof_action=pass:repeatlast=0:x=0:y=960'
        stream_id += 1
        if video_camera_count > stream_id:
            ffmpeg_filter += f'[layer{stream_id}];'

    if 'back' in video_cameras:
        cmd_line += ['-i', video_cameras['back']]
        ffmpeg_filter += f'[{stream_id}:v]setpts=PTS-STARTPTS[back];'
        ffmpeg_filter += f'[layer{stream_id}][back]overlay=eof_action=pass:repeatlast=0:x=1280:y=960'

    codec_name, codec_options = codec
    cmd_line += [
        '-filter_complex', ffmpeg_filter,
        '-c:v', codec_name, *codec_options,
        '-r', '36',  # average frame rate based on existing tesla cam videos
        '-v', 'error',
        '-y',
        layout_video_file_path,
    ]
    return cmd_line


def create_layout_video_file_path(working_layout_folder_path, file_basename):
    ' Return the full path to a layout video file '
    return os.path.join(working_layout_folder_path, file_basename + '.mp4')


async def create_layout_video_process(
    video_file_info,
    ffmpeg_file_path,
    codec,
    working_layout_folder_path,
):
    ' FFMPEG process to merge camera video segments into one video segment '
    layout_video_file_path = create_layout_video_file_path(
        working_layout_folder_path,
        video_file_info[0]
    )
    video_file_stream_info = video_file_info[1]
    cmd_line = generate_layout_command_line(
        ffmpeg_file_path,
        codec,
        video_file_stream_info,
        layout_video_file_path
    )
    LOGGER.info('creating layout video %s', layout_video_file_path)
    proc = await asyncio.create_subprocess_exec(*cmd_line)
    await proc.wait()
    if proc.returncode:
        raise subprocess.CalledProcessError(proc.returncode, cmd=' '.join(cmd_line))

    LOGGER.info('finished layout video %s', layout_video_file_path)


async def create_layout_video(
    video_file_info,
    ffmpeg_file_path,
    encoder_factory,
    codec,
    working_layout_folder_path
):
    ' Create a layout video that merges all the cameras '
    async with encoder_factory.reserve_encoder():
        await create_layout_video_process(
            video_file_info,
            ffmpeg_file_path,
            codec,
            working_layout_folder_path
        )


async def create_layout_videos(
    video_file_info_list,
    ffmpeg_file_path,
    encoder_factory,
    codec,
    working_layout_folder_path
):
    ' Create multiple layout videos concurrently '
    await asyncio.gather(
        *(
            create_layout_video(
                video_file_info,
                ffmpeg_file_path,
                encoder_factory,
                codec,
                working_layout_folder_path,
            )
            for video_file_info in video_file_info_list
        )
    )


async def create_file_manifest(video_file_map, working_layout_folder_path):
    ' Create an ffmpeg file manifest for merging '
    manifest_file_path = os.path.join(working_layout_folder_path, 'concat_manifest.txt')
    with open(manifest_file_path, 'w') as manifest_file:
        for file_basename in sorted(video_file_map.keys()):
            layout_video_file_path = create_layout_video_file_path(
                working_layout_folder_path, file_basename
            )
            print(f"file '{layout_video_file_path}'", file=manifest_file)
    return manifest_file_path


async def concatenate_layout_videos(ffmpeg_file_path, manifest_file_path, output_file_path):
    ' Concatenate video segments into one video file per video folder '
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    cmd_line = [
        ffmpeg_file_path,  # full path to merge tool
        '-v', 'warning',
        '-y',  # Overwrite existing output files
        '-f', 'concat', '-safe', '0', # Only concatenate and allow unsafe paths
        '-i', manifest_file_path,
        '-c', 'copy',  # Do not re-encode for the output
        output_file_path,  # full path to output file
    ]
    LOGGER.info('create merge process for %s', output_file_path)
    proc = await asyncio.create_subprocess_exec(*cmd_line)
    await proc.wait()
    if proc.returncode:
        raise subprocess.CalledProcessError(proc.returncode, cmd=' '.join(cmd_line))
    LOGGER.info('completed merge process for %s', output_file_path)


async def create_video_file(
    ffprobe_file_path,
    ffmpeg_file_path,
    encoder_factory,
    codec,
    input_folder_path,
    output_folder_path,
    intermediate_folder_path,
):
    ' Merge a single folder of videos into one continuous video '
    video_file_map = await create_video_file_map(
        ffprobe_file_path,
        input_folder_path,
        output_folder_path
    )
    if not video_file_map:
        return

    base_name = os.path.basename(input_folder_path)
    working_layout_folder_path = os.path.join(intermediate_folder_path, base_name)
    os.makedirs(working_layout_folder_path)

    await create_layout_videos(
        video_file_map.items(),
        ffmpeg_file_path,
        encoder_factory,
        codec,
        working_layout_folder_path
    )
    manifest_file_path = await create_file_manifest(
        video_file_map,
        working_layout_folder_path
    )

    output_file_path = os.path.join(output_folder_path, f'{base_name}.mp4')
    await concatenate_layout_videos(ffmpeg_file_path, manifest_file_path, output_file_path)


class EncoderPool:
    def __init__(self, number_of_encoders):
        self._current_encoder_count = number_of_encoders

    @contextlib.asynccontextmanager
    async def reserve_encoder(self):
        ' Wait until an encoder is available '
        try:
            while self._current_encoder_count <= 0:
                await asyncio.sleep(1)

            self._current_encoder_count -= 1
            yield
        finally:
            self._current_encoder_count += 1


def yield_input_folder_paths(base_input_folder_path):
    ' Enumerate folder to yield subfolders to process '
    input_folder_names = os.listdir(base_input_folder_path)
    if os.path.isdir(os.path.join(base_input_folder_path, input_folder_names[0])):
        for input_folder_name in input_folder_names:
            yield os.path.join(base_input_folder_path, input_folder_name)
    else:
        yield base_input_folder_path


async def create_video_files(
    ffmpeg_folder_path,
    number_of_encoders,
    codec,
    base_input_folder_path,
    base_output_folder_path,
    intermediate_folder_path,
):
    ' Concurrently merge multiple folders of videos into individual continuous videos '
    ffprobe_file_path = os.path.join(ffmpeg_folder_path, 'ffprobe.exe')
    ffmpeg_file_path = os.path.join(ffmpeg_folder_path, 'ffmpeg.exe')

    encoder_factory = EncoderPool(number_of_encoders)
    folder_paths = yield_input_folder_paths(base_input_folder_path)
    await asyncio.gather(
        *(
            create_video_file(
                ffprobe_file_path,
                ffmpeg_file_path,
                encoder_factory,
                codec,
                input_folder_path,
                base_output_folder_path,
                intermediate_folder_path,
            )
            for input_folder_path in folder_paths
        )
    )


def extract_videos(
    ffmpeg_folder_path,
    number_of_encoders,
    codec,
    base_input_folder_path,
    base_output_folder_path,
    keep_temp_folder,
):
    ' Extract videos from a folder using a temporary work area '
    def _extract(intermediate_folder_path):
        asyncio.run(
            create_video_files(
                ffmpeg_folder_path,
                number_of_encoders,
                codec,
                base_input_folder_path,
                base_output_folder_path,
                intermediate_folder_path,
            )
        )

    if keep_temp_folder:
        intermediate_folder_path = tempfile.mkdtemp(dir=base_output_folder_path)
        _extract(intermediate_folder_path)
    else:
        with tempfile.TemporaryDirectory(dir=base_output_folder_path) as intermediate_folder_path:
            _extract(intermediate_folder_path)


def main():
    ' Main entry point '
    extract_videos_arguments = arg_parser.get_arguments()
    execution_time = timeit.timeit(
        lambda : extract_videos(*extract_videos_arguments),
        setup='gc.enable()', # Re-enable garbage collection
        number=1
    )
    duration = time_duration.seconds_to_units(execution_time)
    print(f'Completed in {duration}')


if __name__ == '__main__':
    main()
