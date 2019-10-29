' Custom types '
import collections

LayoutOptions = collections.namedtuple(
    'LayoutOptions',
    [
        'codec', # Codec as a string
        'preset', # Codec preset as a string
        'layout', # Layout name as a string
        'reduce', # Percentage value from 1 to 100 as a float
    ]
)

# All structures here hold full filepaths
FFMpegPaths = collections.namedtuple(
    'FFMpegPaths',
    ['ffprobe', 'ffmpeg']
)

WorkingFolderPaths = collections.namedtuple(
    'WorkingFolderPaths',
    ['input', 'output', 'intermediate']
)

BaseFolderPaths = collections.namedtuple(
    'BaseFolderPaths',
    ['input', 'output']
)
