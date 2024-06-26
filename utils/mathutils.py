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


def IsFloat(element: any) -> bool:
    if element is None:
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False


def GetPercentageValue(value: float, min_value: float, max_value: float):
    return (value - min_value) / (max_value - min_value)


def GetInversePercentageValue(value: float, min_value: float, max_value: float):
    return 1 - GetPercentageValue(value, min_value, max_value)


def GetValueFromPercentage(percentage: float, min_value: float, max_value: float):
    return (max_value - min_value) * percentage + min_value


def ClosestNumber(n: int, m: int):
    q = n // m
    n1 = m * q

    if (n * m) > 0:
        n2 = m * (q + 1)
    else:
        n2 = m * (q - 1)

    if abs(n-n1) < abs(n-n2):
        return n1
    return n2
