import pymunk
from typing import List
from pygame import Vector2
from pymunk import Vec2d
from data.constants import SF_WALL, COLLTYPE_TRACK, COLLTYPE_GUIDEPOINT, TRACK_PADDING
from data.files import ASSETS_DIR, SPRITES_DIR


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


def _ParseTrackCoordinates(coordinate_set: str):
    coordinate_split = coordinate_set.split(",")
    return Vec2d(int(coordinate_split[0]), int(coordinate_split[1]))


class Track(object):
    def __init__(
            self,
            name: str,
            sprite_filename: str,
            start_position: dict[_StartPosition],
            left_wall: list[str],
            right_wall: list[str],
            guidepoints: list[list[str]],
            checkpoints: list[int]):
        self.name = name
        self.sprite_path = ASSETS_DIR + SPRITES_DIR + sprite_filename
        self.start_position = _StartPosition(**start_position)
        self.left_wall: List[Vec2d] = []
        self.right_wall: List[Vec2d] = []
        self.guidepoints: List[tuple[Vec2d, Vec2d]] = []
        self.checkpoints = checkpoints

        for vec_string in left_wall:
            self.left_wall.append(_ParseTrackCoordinates(vec_string))
        for vec_string in right_wall:
            self.right_wall.append(_ParseTrackCoordinates(vec_string))
        for vec_string_tuple in guidepoints:
            self.guidepoints.append((_ParseTrackCoordinates(vec_string_tuple[0]),
                                     _ParseTrackCoordinates(vec_string_tuple[1])))

        max_x = 0
        max_y = 0
        for vec in self.left_wall:
            max_x = max(max_x, vec.x)
            max_y = max(max_y, vec.y)
        for vec in self.right_wall:
            max_x = max(max_x, vec.x)
            max_y = max(max_y, vec.y)

        self.size = Vector2(max_x + TRACK_PADDING, max_y + TRACK_PADDING)

    def AddToSpace(self, space: pymunk.Space):
        track_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        track_body.position = (0, 0)
        track_segments = []
        for i in range(len(self.left_wall) - 1):
            segment = pymunk.Segment(track_body, self.left_wall[i], self.left_wall[i + 1], 5)
            segment.filter = pymunk.ShapeFilter(categories=SF_WALL)
            segment.collision_type = COLLTYPE_TRACK
            track_segments.append(segment)
        left_end_segment = pymunk.Segment(track_body, self.left_wall[-1], self.left_wall[0], 5)
        left_end_segment.filter = pymunk.ShapeFilter(categories=SF_WALL)
        left_end_segment.collision_type = COLLTYPE_TRACK
        track_segments.append(left_end_segment)
        for i in range(len(self.right_wall) - 1):
            segment = pymunk.Segment(track_body, self.right_wall[i], self.right_wall[i + 1], 5)
            segment.filter = pymunk.ShapeFilter(categories=SF_WALL)
            segment.collision_type = COLLTYPE_TRACK
            track_segments.append(segment)
        right_end_segment = pymunk.Segment(track_body, self.right_wall[-1], self.right_wall[0], 5)
        right_end_segment.filter = pymunk.ShapeFilter(categories=SF_WALL)
        right_end_segment.collision_type = COLLTYPE_TRACK
        track_segments.append(right_end_segment)
        for guidepoint_tuple in self.guidepoints:
            segment = pymunk.Segment(track_body, guidepoint_tuple[0], guidepoint_tuple[1], 5)
            segment.sensor = True
            segment.collision_type = COLLTYPE_GUIDEPOINT
            track_segments.append(segment)
        space.add(track_body, *track_segments)
