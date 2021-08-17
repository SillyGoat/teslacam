' Unit classes for simple serialization and validation '

class Units:
    ' Multiple units '
    def __init__(self, *units):
        self.units = units

    def __bool__(self):
        return all((True for unit in self.units if unit))

    def __str__(self):
        valid_units = [str(unit) for unit in self.units if unit]
        if valid_units:
            return ', '.join(valid_units)

        return str(self.units[-1])


class Unit:
    ' Single unit '
    def __init__(self, value, value_type):
        self.value = value
        self.value_type = value_type

    def __bool__(self):
        return bool(self.value)

    def __str__(self):
        formatted_value = self.value if self.value < 1 else int(self.value)
        suffix = 's' if formatted_value != 1 else ''
        return f'{formatted_value} {self.value_type}{suffix}'
