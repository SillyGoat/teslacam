' Create video layouts '

def create_layout(video_resolution, layout_offsets):
    ' Create layout using resolution and layout offsets '
    resolved_layout = {}
    width, height = video_resolution
    for layer_name, offsets in layout_offsets.items():
        x_offset, y_offset = offsets
        resolved_layout[layer_name] = (int(width * x_offset), int(height * y_offset))
    return resolved_layout


def create_native_layout(layout_offsets):
    ' Create layout using layout offsets '
    camera_native_resolution = (1280, 960)
    return create_layout(camera_native_resolution, layout_offsets)
