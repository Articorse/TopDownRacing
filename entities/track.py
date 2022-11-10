from typing import List

import pymunk
from pymunk import Vec2d

from data.constants import SF_WALL, COLLTYPE_TRACK, COLLTYPE_CHECKPOINT
from entities.car import Car


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
            start_position: dict[_StartPosition],
            left_wall: list[str],
            right_wall: list[str],
            checkpoints: list[list[str]]):
        self.start_position = _StartPosition(**start_position)
        self.left_wall = left_wall
        self.right_wall = right_wall
        self.checkpoints = checkpoints
        self.checkpoint_data: List[(Vec2d, Vec2d)] = []

    def __str__(self):
        return "{0} {1} {2} {3}".format(self.start_position, self.left_wall, self.right_wall, self.checkpoints)

    def AddToSpace(self, space: pymunk.Space):
        track_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        track_body.position = (0, 0)
        track_segments = []
        for i in range(len(self.left_wall) - 1):
            point_a = _ParseTrackCoordinates(self.left_wall[i])
            point_b = _ParseTrackCoordinates(self.left_wall[i + 1])
            segment = pymunk.Segment(track_body, point_a, point_b, 5)
            segment.filter = pymunk.ShapeFilter(categories=SF_WALL)
            segment.collision_type = COLLTYPE_TRACK
            track_segments.append(segment)
        left_end_segment = pymunk.Segment(
                track_body,
                _ParseTrackCoordinates(self.left_wall[-1]),
                _ParseTrackCoordinates(self.left_wall[0]),
                5)
        left_end_segment.filter = pymunk.ShapeFilter(categories=SF_WALL)
        left_end_segment.collision_type = COLLTYPE_TRACK
        track_segments.append(left_end_segment)
        for i in range(len(self.right_wall) - 1):
            point_a = _ParseTrackCoordinates(self.right_wall[i])
            point_b = _ParseTrackCoordinates(self.right_wall[i + 1])
            segment = pymunk.Segment(track_body, point_a, point_b, 5)
            segment.filter = pymunk.ShapeFilter(categories=SF_WALL)
            segment.collision_type = COLLTYPE_TRACK
            track_segments.append(segment)
        right_end_segment = pymunk.Segment(
                track_body,
                _ParseTrackCoordinates(self.right_wall[-1]),
                _ParseTrackCoordinates(self.right_wall[0]),
                5)
        right_end_segment.filter = pymunk.ShapeFilter(categories=SF_WALL)
        right_end_segment.collision_type = COLLTYPE_TRACK
        track_segments.append(right_end_segment)
        for i in range(len(self.checkpoints)):
            point_a = _ParseTrackCoordinates(self.checkpoints[i][0])
            point_b = _ParseTrackCoordinates(self.checkpoints[i][1])
            segment = pymunk.Segment(track_body, point_a, point_b, 5)
            segment.sensor = True
            segment.collision_type = COLLTYPE_CHECKPOINT
            self.checkpoint_data.append((point_a, point_b))
            track_segments.append(segment)
        space.add(track_body, *track_segments)
