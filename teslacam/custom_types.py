' Custom types '
import collections

LayoutOptions = collections.namedtuple(
    'LayoutOptions',
    ['codec', 'preset', 'layout', 'reduce']
)

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
