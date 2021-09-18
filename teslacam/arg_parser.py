' Argument parser '
import argparse
import pathlib

from . import(
    constants,
    custom_types
)

def valid_percent(value):
    ' Validate percentage values '
    percent = float(value)
    if 0 < percent <= 100:
        return percent
    raise argparse.ArgumentTypeError(f'{value} must be within 1 and 100')


def quoted_choices(choices):
    ' Return a string of quoted choices '
    return ', '.join([f"'{choice}'" for choice in choices])


def str_to_bool(value):
    ' Validate boolean arguments '
    token = value.lower()
    true_values = ['t', 'true', '1']
    if token in true_values:
        return True

    false_values = ['f', 'false', '0']
    if token in false_values:
        return False

    choices = quoted_choices(true_values + false_values)
    raise argparse.ArgumentTypeError(f"invalid choice '{value}' (choose from {choices})")


def get_arguments():
    ' Parse command line arguments '
    parser = argparse.ArgumentParser(
        prog=__package__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'ffprobe_file_path',
        type=pathlib.Path,
        help='Path to the ffprobe binary',
    )
    parser.add_argument(
        'ffmpeg_file_path',
        type=pathlib.Path,
        help='Path to the ffmpeg binary',
    )
    parser.add_argument(
        'input_folder_path',
        type=pathlib.Path,
        help='Path to the video folder containing timestamped folders',
    )
    parser.add_argument(
        'output_folder_path',
        type=pathlib.Path,
        help='Path to the output folder containing both merged files and the temporary work folder',
    )
    parser.add_argument(
        '--codec',
        default='hevc_nvenc',
        help='Codec to use for encoding',
        choices=constants.CODEC_OPTIONS.keys(),
    )
    preset_token = '--preset'
    parser.add_argument(
        preset_token,
        default='slow',
        help='Codec\'s preset to use for encoding.  See ffmpeg -h long for each codec\'s available presets',
    )
    parser.add_argument(
        '--reduce',
        default=constants.DONT_REDUCE,
        help='Percent to reduce video to',
        type=valid_percent,
    )
    parser.add_argument(
        '--layout',
        default='pyramid',
        help='Camera layout',
        choices=constants.LAYOUT_OFFSETS.keys(),
    )
    parser.add_argument(
        '--keep_temp_folder',
        default=False,
        help='Keep temporary working folder after extraction',
        type=str_to_bool,
    )
    parser.add_argument(
        '--log_level',
        default='info',
        help=(
            'Display log messages that matches or exceeds the severity '
            f'of the specified level.  Use "{constants.DISABLE_LOGGING}" '
            'to disable messages'
        ),
        choices=constants.LOG_LEVELS.keys()
    )
    args = parser.parse_args()

    presets = constants.CODEC_OPTIONS[args.codec][0]
    if args.preset not in presets:
        choices = quoted_choices(presets)
        parser.error(
            f"argument {preset_token}: invalid choice: '{args.preset}' (choose from {choices})"
        )

    return (
        constants.LOG_LEVELS[args.log_level],
        (
            custom_types.FFMpegPaths(
                args.ffprobe_file_path,
                args.ffmpeg_file_path,
            ),
            custom_types.LayoutOptions(
                args.codec,
                args.preset,
                args.layout,
                args.reduce,
            ),
            custom_types.BaseFolderPaths(
                args.input_folder_path,
                args.output_folder_path,
            ),
            args.keep_temp_folder,
        )
    )
