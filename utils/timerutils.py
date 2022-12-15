import pygame.time

from data.constants import INT_MAX_VALUE
from data.globalvars import LAST_FRAME_TIME

_timers: dict[str, int] = {}


def FormatTime(time: int):
    if time == INT_MAX_VALUE or time == 0:
        return "-:--:--.---"
    s, ms = divmod(time, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f'{h:d}:{m:02d}:{s:02d}.{ms:03d}'


def WaitTimer(timer_key: str, milliseconds: int, clock: pygame.time.Clock):
    if timer_key not in _timers.keys():
        _timers[timer_key] = 0

    _timers[timer_key] += clock.get_time() - LAST_FRAME_TIME

    if _timers[timer_key] >= milliseconds:
        _timers.pop(timer_key)
        return True

    return False
