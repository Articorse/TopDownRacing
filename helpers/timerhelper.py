def FormatTime(time: int):
    s, ms = divmod(time, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f'{h:d}:{m:02d}:{s:02d}.{ms:03d}'
