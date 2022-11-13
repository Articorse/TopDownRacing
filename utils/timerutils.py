from data.constants import INT_MAX_VALUE


def FormatTime(time: int):
    if time == INT_MAX_VALUE or time == 0:
        return "-:--:--.---"
    s, ms = divmod(time, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f'{h:d}:{m:02d}:{s:02d}.{ms:03d}'
