class Units:
    def __init__(self, *units):
        self.units = units

    def __str__(self):
        valid_units = (str(unit) for unit in self.units if unit)
        return ', '.join(valid_units)


class Unit:
    def __init__(self, value, value_type):
        self.value = value
        self.value_type = value_type

    def __bool__(self):
        return bool(self.value)

    def __str__(self):
        suffix = 's' if self.value != 1 else ''
        return f'{self.value} {self.value_type}{suffix}'
