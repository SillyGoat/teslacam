# Except for background, the key names must match the file name suffixes for the camera data
LAYOUT_OFFSETS = {
    'pyramid': {
        'background': (3, 2),
        'front': (1, 0),
        'right_repeater': (0, 1),
        'back': (1, 1),
        'left_repeater': (2, 1),
    },
    'tall_diamond': {
        'background': (2, 3),
        'front': (.5, 0),
        'right_repeater': (0, 1),
        'back': (.5, 2),
        'left_repeater': (1, 1),
    },
    'short_diamond': {
        'background': (3, 2),
        'front': (1, 0),
        'right_repeater': (0, .5),
        'back': (1, 1),
        'left_repeater': (2, .5),
    },
    'cross': {
        'background': (3, 3),
        'front': (1, 0),
        'right_repeater': (0, 1),
        'back': (1, 2),
        'left_repeater': (2, 1),
    }
}

NVIDIA_PRESETS = (
    'slow',
    'medium',
    'fast',
    'hp',
    'hq',
    'bd',
    'll',
    'llhq',
    'llhp',
    'lossless',
    'losslesshp',
)

LIBX265_PRESETS = (
    'ultrafast',
    'superfast',
    'veryfast',
    'faster',
    'fast',
    'medium',
    'slow',
    'slower',
    'veryslow',
    'placebo',
)

CODEC_OPTIONS = {
    'hevc_nvenc': (
        NVIDIA_PRESETS,
        2, # Typical nvidia GPUs only support 2 simulataneous executions
    ),
    'libx265': (
        LIBX265_PRESETS,
        1, # libx265 already runs in parallel.  no need to thrash the scheduler
    )
}

DONT_REDUCE = 100 # Reduction factor when you don't want to reduce by anything
