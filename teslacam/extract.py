' Tesla camera video post-processing module '
import asyncio
import collections
import json
import logging
import os
import pathlib
import re
import subprocess
import tempfile

from . import(
    asyncio_subprocess,
    constants,
    custom_types
)

LOGGER = logging.getLogger(constants.LOGGER_NAME)

ResourceAcquire = collections.namedtuple(
    'ResourceAcquire',
    [
        'probe',
        'encoder',
    ]
)

async def get_video_stream_info(ffprobe_file_path, video_file_path):
    ' FFMPEG process to retrieve video metadata '
    ffprobe_cmd_line = [
        ffprobe_file_path,
        '-v', 'error',
        '-show_entries', 'stream=duration',
        '-print_format', 'json',
        '-i', video_file_path,
    ]
    LOGGER.debug('start gathering video stream info from %s', video_file_path)
    data = await asyncio_subprocess.check_output(ffprobe_cmd_line)
    LOGGER.debug('completed gathering video stream info from %s', video_file_path)

    return json.loads(data)['streams'][0]


def get_longest_duration(existing_duration, new_duration):
    ' Decide how long a joined camera segment should play '
    if float(existing_duration) >= float(new_duration):
        return existing_duration
    return new_duration


REGEX_VIDEO_FILENAME = re.compile(
    r'(\d\d\d\d-\d\d-\d\d_\d\d-\d\d-\d\d)-(\w+)\.mp4',
    re.IGNORECASE
)


async def populate_video_map(
        video_map,
        ffprobe_file_path,
        acquire_probe,
        video_file_path
):
    ' Retrieve video metadata from raw video files '
    match_result = re.fullmatch(REGEX_VIDEO_FILENAME, video_file_path.name)
    if not match_result:
        LOGGER.info('skip %s because it does not look like a video file', video_file_path)
        return

    async with acquire_probe:
        try:
            video_stream_info = await get_video_stream_info(
                ffprobe_file_path,
                video_file_path
            )

            if not video_stream_info:
                LOGGER.warning('skip %s because it contains no streams', video_file_path)
                return

        except subprocess.CalledProcessError as proc_error:
            LOGGER.warning(
                'skip %s because it ran into the following exception: %s',
                video_file_path,
                proc_error
            )
            return

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
        acquire_probe,
        input_folder_path
):
    ' Enumerates video folder to find files to layout and concatenate '
    video_file_paths = input_folder_path.iterdir()

    video_map = {}
    await asyncio.gather(
        *(
            populate_video_map(
                video_map,
                ffprobe_file_path,
                acquire_probe,
                video_file_path
            )
            for video_file_path in video_file_paths
        )
    )
    LOGGER.info('gathered video info for %s', input_folder_path)
    return video_map


def create_camera_filter_layer(stream_id, location):
    ' Create an ffmpeg filter layer '
    # Create a name for the previous layer and the camera layer
    # Then use both to create this brand new layer
    x_offset, y_offset = location
    return f'[layer{stream_id}];' + \
        f'[{stream_id}:v]setpts=PTS-STARTPTS[camera{stream_id}];' + \
        f'[layer{stream_id}][camera{stream_id}]' + \
            f'overlay=eof_action=pass:repeatlast=0:x={x_offset}:y={y_offset}'


def create_scale_filter(reduce_percentage):
    ' Create a scale filter '
    if reduce_percentage == constants.DONT_REDUCE:
        return ''

    return f'[scalelayer];[scalelayer]scale=iw*{reduce_percentage}/100:-1:flags=bicubic'


def generate_layout_command_line(
        ffmpeg_file_path,
        layout_options,
        video_file_stream_info,
        layout_video_file_path
):
    ' FFMPEG command line that merges camera videos into one '
    layout = constants.LAYOUT[layout_options.layout]
    background_width, background_height = layout['background']
    ffmpeg_filter = f'color=duration={video_file_stream_info["duration"]}:' + \
                    f's={background_width}x{background_height}:' + \
                    'c=black'

    cmd_line = [ffmpeg_file_path]
    for stream_id, camera_info in enumerate(video_file_stream_info['cameras'].items()):
        layer_name, video_camera_file_path = camera_info
        ffmpeg_filter += create_camera_filter_layer(stream_id, layout[layer_name])
        cmd_line += ['-i', video_camera_file_path]

    ffmpeg_filter += create_scale_filter(layout_options.reduce)

    cmd_line += [
        '-filter_complex', ffmpeg_filter,
        '-c:v', layout_options.codec, '-preset', layout_options.preset,
        '-b:v', '8M', # pick a bitrate that's friendly to 1280x960 video
        '-r', '36',  # average frame rate based on existing tesla cam videos
        '-v', 'error', # reduce output noise
        '-y', # overwrite existing file
        layout_video_file_path,
    ]
    return cmd_line


def create_layout_video_file_path(working_layout_folder_path, file_basename):
    ' Return the full path to a layout video file '
    return working_layout_folder_path / f'{file_basename}.mp4'


async def create_layout_video_process(
        video_file_info,
        ffmpeg_file_path,
        layout_options,
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
        layout_options,
        video_file_stream_info,
        layout_video_file_path
    )
    LOGGER.info('creating layout video %s', layout_video_file_path)
    await asyncio_subprocess.check_call(cmd_line)
    LOGGER.info('finished layout video %s', layout_video_file_path)


async def create_layout_video(
        video_file_info,
        ffmpeg_file_path,
        acquire_encoder,
        layout_options,
        working_layout_folder_path
):
    ' Create a layout video that merges all the cameras '
    async with acquire_encoder:
        await create_layout_video_process(
            video_file_info,
            ffmpeg_file_path,
            layout_options,
            working_layout_folder_path
        )


async def create_layout_videos(
        video_file_info_list,
        ffmpeg_file_path,
        acquire_encoder,
        layout_options,
        working_layout_folder_path
):
    ' Create multiple layout videos concurrently '
    await asyncio.gather(
        *(
            create_layout_video(
                video_file_info,
                ffmpeg_file_path,
                acquire_encoder,
                layout_options,
                working_layout_folder_path,
            )
            for video_file_info in video_file_info_list
        )
    )


async def create_file_manifest(video_file_map, working_layout_folder_path):
    ' Create an ffmpeg file manifest for merging '
    manifest_file_path = working_layout_folder_path / 'concat_manifest.txt'
    with open(manifest_file_path, 'w') as manifest_file:
        for file_basename in sorted(video_file_map.keys()):
            layout_video_file_path = create_layout_video_file_path(
                working_layout_folder_path,
                file_basename
            )
            print(f"file '{layout_video_file_path}'", file=manifest_file)
    return manifest_file_path


async def concatenate_layout_videos(ffmpeg_file_path, manifest_file_path, output_file_path):
    ' Concatenate video segments into one video file per video folder '
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    cmd_line = [
        ffmpeg_file_path,  # full path to merge tool
        '-v', 'warning',
        '-y',  # Overwrite existing output files
        '-f', 'concat', '-safe', '0', # Only concatenate and allow unsafe paths
        '-i', manifest_file_path,
        '-c', 'copy',  # Do not re-encode for the output
        output_file_path,  # full path to output file
    ]
    LOGGER.debug('concatenate videos for %s', output_file_path)
    await asyncio_subprocess.check_call(cmd_line)
    LOGGER.info('concatenation completed for %s', output_file_path)


async def create_video_file(
        ffmpeg_paths,
        resource_acquire,
        layout_options,
        working_folder_paths,
):
    ' Merge a single folder of videos into one continuous video '
    video_file_map = await create_video_file_map(
        ffmpeg_paths.ffprobe,
        resource_acquire.probe,
        working_folder_paths.input
    )
    if not video_file_map:
        return

    base_name = working_folder_paths.input.name
    working_layout_folder_path = working_folder_paths.intermediate / base_name
    working_layout_folder_path.mkdir()

    await create_layout_videos(
        video_file_map.items(),
        ffmpeg_paths.ffmpeg,
        resource_acquire.encoder,
        layout_options,
        working_layout_folder_path
    )
    manifest_file_path = await create_file_manifest(
        video_file_map,
        working_layout_folder_path
    )

    output_file_path = working_folder_paths.output / f'{base_name}.mp4'
    await concatenate_layout_videos(ffmpeg_paths.ffmpeg, manifest_file_path, output_file_path)


async def create_video_files(
        ffmpeg_paths,
        layout_options,
        working_folder_paths,
):
    ' Concurrently merge multiple folders of videos into individual continuous videos '
    # Limit resources using semaphores to stop exhaustion and thrashing
    resource_acquire = ResourceAcquire(
        asyncio.Semaphore(os.cpu_count()),
        asyncio.Semaphore(constants.CODEC_OPTIONS[layout_options.codec][1]),
    )
    await asyncio.gather(
        *(
            create_video_file(
                ffmpeg_paths,
                resource_acquire,
                layout_options,
                custom_types.WorkingFolderPaths(
                    input_folder_path,
                    working_folder_paths.output,
                    working_folder_paths.intermediate,
                )
            )
            for input_folder_path in working_folder_paths.input.iterdir()
        )
    )


async def shutdown():
    ' Cleanup tasks '
    LOGGER.info('cancel outstanding tasks')
    non_current_tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]

    for non_current_task in non_current_tasks:
        non_current_task.cancel()

    LOGGER.info('cancelling %s outstanding tasks', len(non_current_tasks))
    # Absorb asyncio.exceptions.CancelledError by setting return_exceptions to True
    await asyncio.gather(*non_current_tasks, return_exceptions=True)
    LOGGER.info('tasks cancelled')


def extract_videos(
        ffmpeg_paths,
        layout_options,
        base_folder_paths,
        keep_temp_folder,
):
    ' Extract videos from a folder using a temporary work area '
    async def _async_extract(intermediate_folder_path):
        try:
            await create_video_files(
                ffmpeg_paths,
                layout_options,
                custom_types.WorkingFolderPaths(
                    *base_folder_paths,
                    intermediate_folder_path,
                ),
            )
        except Exception:
            await shutdown()
            raise

    if keep_temp_folder:
        intermediate_folder_path = pathlib.Path(tempfile.mkdtemp(dir=base_folder_paths.output))
        asyncio.run(_async_extract(intermediate_folder_path))
    else:
        with tempfile.TemporaryDirectory(dir=base_folder_paths.output) as intermediate_folder_path:
            asyncio.run(_async_extract(pathlib.Path(intermediate_folder_path)))
