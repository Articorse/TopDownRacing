from enum import Enum


class RaceDirection(str, Enum):
    Up = 'Up'
    Right = 'Right'
    Down = 'Down'
    Left = 'Left'

    @classmethod
    def has_value(cls, value):
        return value in set(item.value for item in RaceDirection)
