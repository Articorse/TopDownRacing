class _Pos(object):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self):
        return "{0} {1}".format(self.x, self.y)


class _StartPosition(object):
    def __init__(self, pos: dict[_Pos], angle: float):
        self.pos = _Pos(**pos)
        self.angle = angle

    def __str__(self):
        return "{0} {1}".format(self.pos, self.angle)


class Track(object):
    def __init__(self, start_position: dict[_StartPosition], left_wall: list[str], right_wall: list[str]):
        self.start_position = _StartPosition(**start_position)
        self.left_wall = left_wall
        self.right_wall = right_wall

    def __str__(self):
        return "{0} {1} {2}".format(self.start_position, self.left_wall, self.right_wall)
