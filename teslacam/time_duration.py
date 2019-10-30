' Time Conversion '

from teslacam.unit import Unit, Units

def seconds_to_units(seconds):
    ' Convert seconds into days, hours, minutes, seconds '
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return Units(
        Unit(days, 'day'),
        Unit(hours, 'hour'),
        Unit(minutes, 'minute'),
        Unit(seconds, 'second'),
    )
