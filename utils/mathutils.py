import math
import pymunk
from pymunk import Vec2d


def AngleToPoint(source_pos: pymunk.Vec2d, source_angle: float, point: Vec2d, offset: bool = True):
    angle_to_point = ((point - source_pos).angle_degrees - math.degrees(source_angle)) % 360
    if offset and angle_to_point > 180:
        angle_to_point -= 360
    return angle_to_point


def IsPointInArc(source_pos: pymunk.Vec2d, source_angle: float, point: Vec2d, arc: float):
    angle_to_point = AngleToPoint(source_pos, source_angle, point)
    half_arc = arc / 2
    return 0 < (half_arc + angle_to_point) % 360 < half_arc * 2
