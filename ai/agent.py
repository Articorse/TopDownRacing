import math
from enum import Enum
from typing import List, Optional

import pygame
import pymunk
from pygame.font import Font
from pymunk import Vec2d

from data.constants import AI_RAY_LENGTH, AI_SIDE_RAY_COUNT, AI_RAY_ANGLE, SF_WALL, AI_RAY_DROPOFF, \
    AI_ANGLE_TO_GUIDEPOINT, SF_CAR_INACTIVE, SF_CAR, AI_ON, AI_GUIDEPOINT_VISUALIZATION_LENGTH, \
    COLLTYPE_LEFT_TURN_COLLIDER, COLLTYPE_RIGHT_TURN_COLLIDER, COLLTYPE_TURN_AUX_COLLIDER, \
    AI_SQUARE_COLLIDER_OFFSET, AI_TURN_COLLIDER_RADIUS_MODIFIER, AI_TURN_COLLIDER_OFFSET_MODIFIER
from entities.car import Car
from entities.track import Track
from utils.mathutils import IsPointInArc, AngleToPoint
from utils.uiutils import DrawText


class _AgentState(Enum):
    Thinking = 0
    Following_Path = 1
    Turning_Left = 2
    Turning_Right = 3
    Reverse_Left = 4
    Reverse_Right = 5
    Reverse = 6


# class _Weight:
#     def __init__(self, axis_value: float, weight: float):
#         self.direction = direction
#         self.axis_value = axis_value
#         self.weight = weight


class Agent:
    def __init__(self, space: pymunk.Space, car: Car, track: Track):
        self.car = car
        self.track = track
        self._space = space
        self.ray_hits: List[tuple[Vec2d, bool, int]] = []
        self.current_checkpoint = 1
        self.current_guidepath_index = 1
        # self._weights = {
        #     "accelerate": _Weight(Direction.Forward, 1.0, 0),
        #     "reverse": _Weight(Direction.Forward, -1.0, 0),
        #     "left": _Weight(Direction.Right, -1.0, 0),
        #     "right": _Weight(Direction.Right, 1.0, 0),
        # }
        self.is_enabled = AI_ON
        self.debug_rays = []
        self.state: _AgentState = _AgentState.Thinking

        turn_collider_radius = (AI_TURN_COLLIDER_RADIUS_MODIFIER / car.car_model.handling) + car.size[1] / 2
        turn_collider_offset = AI_TURN_COLLIDER_OFFSET_MODIFIER / car.car_model.handling

        left_turn_collider = pymunk.Circle(
            car.body, turn_collider_radius,
            (0, -turn_collider_offset))
        left_turn_collider.sensor = True
        left_turn_collider.collision_type = COLLTYPE_LEFT_TURN_COLLIDER
        left_turn_collider.filter = pymunk.ShapeFilter(mask=SF_WALL)
        self.left_turn_collider = left_turn_collider

        right_turn_collider = pymunk.Circle(
            car.body, turn_collider_radius,
            (0, turn_collider_offset))
        right_turn_collider.sensor = True
        right_turn_collider.collision_type = COLLTYPE_RIGHT_TURN_COLLIDER
        right_turn_collider.filter = pymunk.ShapeFilter(mask=SF_WALL)
        self.right_turn_collider = right_turn_collider

        left_front_collider = pymunk.Poly(car.body, (
            car.body.position,
            car.body.position + (0, -(turn_collider_radius * 2 - car.size[1] / 2)),
            car.body.position + (turn_collider_radius, -(turn_collider_radius * 2 - car.size[1] / 2)),
            car.body.position + (turn_collider_radius, 0)))
        left_front_collider.sensor = True
        left_front_collider.collision_type = COLLTYPE_TURN_AUX_COLLIDER
        left_front_collider.filter = pymunk.ShapeFilter(mask=SF_WALL)
        self.left_front_collider = left_front_collider

        right_front_collider = pymunk.Poly(car.body, (
            car.body.position,
            car.body.position + (0, turn_collider_radius * 2 - car.size[1] / 2),
            car.body.position + (turn_collider_radius, turn_collider_radius * 2 - car.size[1] / 2),
            car.body.position + (turn_collider_radius, 0)))
        right_front_collider.sensor = True
        right_front_collider.collision_type = COLLTYPE_TURN_AUX_COLLIDER
        right_front_collider.filter = pymunk.ShapeFilter(mask=SF_WALL)
        self.right_front_collider = right_front_collider

        left_back_collider = pymunk.Poly(car.body, (
            car.body.position,
            car.body.position + (0, -(turn_collider_radius * 2 - car.size[1] / 2)),
            car.body.position + (-turn_collider_radius, -(turn_collider_radius * 2 - car.size[1] / 2)),
            car.body.position + (-turn_collider_radius, 0)))
        left_back_collider.sensor = True
        left_back_collider.collision_type = COLLTYPE_TURN_AUX_COLLIDER
        left_back_collider.filter = pymunk.ShapeFilter(mask=SF_WALL)
        self.left_back_collider = left_back_collider

        right_back_collider = pymunk.Poly(car.body, (
            car.body.position,
            car.body.position + (0, turn_collider_radius * 2 - car.size[1] / 2),
            car.body.position + (-turn_collider_radius, turn_collider_radius * 2 - car.size[1] / 2),
            car.body.position + (-turn_collider_radius, 0)))
        right_back_collider.sensor = True
        right_back_collider.collision_type = COLLTYPE_TURN_AUX_COLLIDER
        right_back_collider.filter = pymunk.ShapeFilter(mask=SF_WALL)
        self.right_back_collider = right_back_collider

        self.left_front_collision: tuple[bool, float] = (False, 0)
        self.left_back_collision: tuple[bool, float] = (False, 0)
        self.right_front_collision: tuple[bool, float] = (False, 0)
        self.right_back_collision: tuple[bool, float] = (False, 0)

        space.remove(car.body)
        space.add(car.body, left_turn_collider, right_turn_collider, left_front_collider,
                  left_back_collider, right_front_collider, right_back_collider)

    def Update(self):
        # cast rays
        self.ray_hits.clear()
        self.debug_rays.clear()

        # pick next guidepath point
        next_gp_index = (self.current_guidepath_index + 1) % len(self.track.guidepath)
        if self.car.body.position.get_dist_sqrd(self.track.guidepath[self.current_guidepath_index]) > \
                self.car.body.position.get_dist_sqrd(self.track.guidepath[next_gp_index]):
            self.current_guidepath_index = next_gp_index
            next_gp_index = (self.current_guidepath_index + 1) % len(self.track.guidepath)
        gp = self.track.guidepath[next_gp_index]

        self.debug_rays.append((gp, (255, 150, 0)))
        if self.is_enabled:
            self.ray_hits.append((self.car.body.position + self.car.facing_vector * AI_RAY_LENGTH, False, 0))
            for i in range(0, AI_SIDE_RAY_COUNT):
                self.ray_hits.append((
                    self.car.body.position +
                    self.car.facing_vector.rotated(AI_RAY_ANGLE * (i + 1)) *
                    (AI_RAY_LENGTH - AI_RAY_DROPOFF * i),
                    False, 0))
                self.ray_hits.append((
                    self.car.body.position +
                    self.car.facing_vector.rotated(-AI_RAY_ANGLE * (i + 1)) *
                    (AI_RAY_LENGTH - AI_RAY_DROPOFF * i),
                    False, 0))
            self.car.shape.filter = pymunk.ShapeFilter(categories=SF_CAR_INACTIVE)
            for i in range(len(self.ray_hits)):
                sq_wall = self._space.segment_query_first(
                    self.car.body.position,
                    self.ray_hits[i][0],
                    1,
                    pymunk.ShapeFilter(mask=SF_WALL))
                sq_car = self._space.segment_query_first(
                    self.car.body.position,
                    self.ray_hits[i][0],
                    1,
                    pymunk.ShapeFilter(mask=SF_CAR))
                if sq_wall:
                    self.ray_hits[i] = (Vec2d(sq_wall.point.x, sq_wall.point.y), True, SF_WALL)
                if sq_car:
                    self.ray_hits[i] = (Vec2d(sq_car.point.x, sq_car.point.y), True, SF_CAR)
            self.car.shape.filter = pymunk.ShapeFilter(categories=SF_CAR)

            # AI
            # if guidepoint is not within sight, loop back through all points until one is within sight
            sq = self._space.segment_query_first(
                self.car.body.position, gp, 1,
                pymunk.ShapeFilter(mask=SF_WALL))
            if sq:
                self.current_guidepath_index -= 2
                if self.current_guidepath_index < 0:
                    self.current_guidepath_index = len(self.track.guidepath) - 1
                if self.current_guidepath_index >= len(self.track.guidepath):
                    self.current_guidepath_index - len(self.track.guidepath)
            gp_is_in_arc = IsPointInArc(self.car.body.position, self.car.body.angle, gp, AI_ANGLE_TO_GUIDEPOINT)

            # state machine
            if self.state == _AgentState.Thinking:
                # switch to Following_Path if
                # 1. guidepoint is within sight
                # 2. guidepoint is in an arc in front of the car
                if not sq and gp_is_in_arc:
                    self.state = _AgentState.Following_Path
                else:
                    if self.left_front_collision[0] and self.right_front_collision[0]:
                        self.state = _AgentState.Reverse
                    else:
                        # check whether turning left or right is closer to facing the guidepoint
                        angle_to_point = AngleToPoint(self.car.body.position, self.car.body.angle, gp)
                        if angle_to_point < 0:
                            if not self.left_front_collision[0]:
                                # switch to Turning_Left if left front collider is clear
                                self.state = _AgentState.Turning_Left
                            elif not self.right_front_collision[0]:
                                # switch to Turning_Right if right front collider is clear
                                self.state = _AgentState.Turning_Right
                            elif not self.right_back_collision[0]:
                                # switch to Reverse_Right if right back collider is clear
                                self.state = _AgentState.Reverse_Right
                            else:
                                # switch to Reverse_Left
                                self.state = _AgentState.Reverse_Left
                        else:
                            if not self.right_front_collision[0]:
                                # switch to Turning_Right if right front collider is clear
                                self.state = _AgentState.Turning_Right
                            elif not self.left_front_collision[0]:
                                # switch to Turning_Left if left front collider is clear
                                self.state = _AgentState.Turning_Left
                            elif not self.left_back_collision[0]:
                                # switch to Reverse_Left if left back collider is clear
                                self.state = _AgentState.Reverse_Left
                            else:
                                # switch to Reverse_Right
                                self.state = _AgentState.Reverse_Right
            elif self.state == _AgentState.Following_Path:
                if sq or not gp_is_in_arc:
                    self.state = _AgentState.Thinking
                # follow path
                angle_to_point = AngleToPoint(self.car.body.position, self.car.body.angle, gp)
                self.car.Accelerate(1.0)
                # try to pass cars in front
                if (self.ray_hits[2][1] and self.ray_hits[2][2] == SF_CAR) or \
                        (self.ray_hits[4][1] and self.ray_hits[4][2] == SF_CAR):
                    self.car.Steer(1)
                elif (self.ray_hits[1][1] and self.ray_hits[1][2] == SF_CAR) or \
                        (self.ray_hits[3][1] and self.ray_hits[3][2] == SF_CAR):
                    self.car.Steer(-1)
                else:
                    steer_power = angle_to_point / (AI_ANGLE_TO_GUIDEPOINT / 2)
                    if self.car.body.velocity.dot(
                            self.car.body.local_to_world((1, 0)) - self.car.body.position) > 0:
                        self.car.Steer(steer_power)
                    else:
                        self.car.Steer(-steer_power)
            elif self.state == _AgentState.Turning_Left:
                # move forward and left
                self.car.Steer(-1.0)
                self.car.Accelerate(0.7)
                if gp_is_in_arc or self.left_front_collision[0]:
                    self.state = _AgentState.Thinking
            elif self.state == _AgentState.Turning_Right:
                # move forward and right
                self.car.Steer(1.0)
                self.car.Accelerate(0.7)
                if gp_is_in_arc or self.right_front_collision[0]:
                    self.state = _AgentState.Thinking
            elif self.state == _AgentState.Reverse_Left:
                # move back and left
                self.car.Steer(-1.0)
                self.car.Accelerate(-0.7)
                if gp_is_in_arc or self.left_back_collision[0]:
                    self.state = _AgentState.Thinking
            elif self.state == _AgentState.Reverse_Right:
                # move back and right
                self.car.Steer(1.0)
                self.car.Accelerate(-0.7)
                if gp_is_in_arc or self.right_back_collision[0]:
                    self.state = _AgentState.Thinking
            elif self.state == _AgentState.Reverse:
                # move back and right
                self.car.Accelerate(-1.0)
                if not self.left_front_collision[0] or not self.right_front_collision[0]:
                    self.state = _AgentState.Thinking

            # TODO: Reimplement as a dumb AI for a dumb car
            """
            # DEBUG START
            if globalvars.ENVIRONMENT_DEBUG:
                min_angle = math.degrees(self.car.body.angle) - AI_ANGLE_TO_GUIDEPOINT / 2
                self.debug_rays.append(
                    (self.car.body.position + Vec2d(AI_GUIDEPOINT_VISUALIZATION_LENGTH, 0).rotated_degrees(min_angle),
                     (100, 255, 255)))
                max_angle = math.degrees(self.car.body.angle) + AI_ANGLE_TO_GUIDEPOINT / 2
                self.debug_rays.append(
                    (self.car.body.position + Vec2d(AI_GUIDEPOINT_VISUALIZATION_LENGTH, 0).rotated_degrees(max_angle),
                     (100, 255, 255)))
            # DEBUG END

            # navigate car
            self._weights = {
                "accelerate": _Weight(Direction.Forward, 1.0, 0),
                "reverse": _Weight(Direction.Forward, -1.0, 0),
                "left": _Weight(Direction.Right, -1.0, 0),
                "right": _Weight(Direction.Right, 1.0, 0),
            }

            if not self.ray_hits[0][1] or\
                    not self.ray_hits[1][1] or\
                    not self.ray_hits[2][1] or\
                    not self.ray_hits[3][1] or\
                    not self.ray_hits[4][1]:
                self._weights["accelerate"].weight += 1

            for i in range(1, len(self.ray_hits)):
                if i % 2 == 1:
                    if self.ray_hits[i][1]:
                        self._weights["left"].weight += 1 / (i + 2)
                else:
                    if self.ray_hits[i][1]:
                        self._weights["right"].weight += 1 / (i + 1)

            # max_weight_key = max(self._weights, key=lambda x: self._weights.get(x).weight)
            # max_weight_keys = [key for index, (key, value) in
            #                    enumerate(self._weights.items()) if
            #                    value.weight == self._weights[max_weight_key]
            #                    .weight]
            if self._weights["accelerate"].weight > self._weights["reverse"].weight:
                self.car.Move(self._weights["accelerate"].direction, self._weights["accelerate"].axis_value)
            elif self._weights["reverse"].weight > self._weights["accelerate"].weight:
                self.car.Move(self._weights["reverse"].direction, self._weights["reverse"].axis_value)
            if self._weights["left"].weight > self._weights["right"].weight:
                self.car.Move(self._weights["left"].direction, self._weights["left"].axis_value)
            elif self._weights["right"].weight > self._weights["left"].weight:
                self.car.Move(self._weights["right"].direction, self._weights["right"].axis_value)
            """

# DEBUG START
    def DebugDrawRays(self, screen: pygame.Surface, camera: (int, int)):
        if self.is_enabled:
            for ray_hit in self.ray_hits:
                if ray_hit[1]:
                    color = (255, 0, 0)
                else:
                    color = (0, 255, 0)
                pygame.draw.line(screen, color, self.car.body.position + camera, ray_hit[0] + camera)
            for debug_ray in self.debug_rays:
                pygame.draw.line(screen, debug_ray[1], self.car.body.position + camera, debug_ray[0] + camera)

    def DebugDrawInfo(self, screen: pygame.Surface, font: Font):
        if screen and font:
            pos = (20, 220)
            DrawText("Checkpoint: " + str(self.current_checkpoint), screen, font, pos)
# DEBUG END
