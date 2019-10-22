from unit import Unit, Units

def seconds_to_units(seconds):
    ' Convert seconds into days, hours, minutes, seconds '
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return Units(
        Unit(int(hours), 'hour'),
        Unit(int(minutes), 'minute'),
        Unit(int(seconds), 'second'),
    )
