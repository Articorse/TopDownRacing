import pygame
import pymunk
from pygame import Vector2
from pygame.font import Font
from data.constants import AI_RAY_LENGTH, AI_SIDE_RAY_COUNT, AI_RAY_ANGLE, SF_WALL, AI_RAY_DROPOFF
from data.enums import Direction
from entities.car import Car
from entities.track import Track


class _Weight:
    def __init__(self, direction: Direction, axis_value: float, weight: float):
        self.direction = direction
        self.axis_value = axis_value
        self.weight = weight


class Agent:
    def __init__(self, space: pymunk.Space, car: Car, track: Track, screen: pygame.Surface = None, font: Font = None):
        self.car = car
        self.track = track
        self._space = space
        self.ray_hits = []
        self.screen = screen
        self._font = font
        self._weights = {
            "accelerate": _Weight(Direction.Forward, 1.0, 0),
            "reverse": _Weight(Direction.Forward, -1.0, 0),
            "left": _Weight(Direction.Right, -1.0, 0),
            "right": _Weight(Direction.Right, 1.0, 0),
        }
        self.is_enabled = True

    def Update(self):
        # cast rays
        if self.is_enabled:
            self.ray_hits.clear()
            self.ray_hits.append((self.car.body.position + self.car.facing_vector * AI_RAY_LENGTH, False))
            for i in range(0, AI_SIDE_RAY_COUNT):
                self.ray_hits.append((
                    self.car.body.position +
                    self.car.facing_vector.rotated(AI_RAY_ANGLE * (i + 1)) *
                    (AI_RAY_LENGTH - AI_RAY_DROPOFF * i),
                    False))
                self.ray_hits.append((
                    self.car.body.position +
                    self.car.facing_vector.rotated(-AI_RAY_ANGLE * (i + 1)) *
                    (AI_RAY_LENGTH - AI_RAY_DROPOFF * i),
                    False))
            for i in range(len(self.ray_hits)):
                sq = self._space.segment_query_first(
                    self.car.body.position,
                    self.ray_hits[i][0],
                    1,
                    pymunk.ShapeFilter(mask=SF_WALL))
                if sq:
                    self.ray_hits[i] = (Vector2(sq.point.x, sq.point.y), True)

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

    def DebugDrawRays(self, screen: pygame.Surface, camera: (int, int)):
        for ray_hit in self.ray_hits:
            if ray_hit[1]:
                color = (255, 0, 0)
            else:
                color = (0, 255, 0)
            pygame.draw.line(screen, color, self.car.body.position + camera, ray_hit[0] + camera)

    def DebugDrawInfo(self):
        if self.screen and self._font:
            pos = (20, 220)
            for weight in self._weights:
                t = self._font.render(weight + ": " + str(round(self._weights[weight].weight, 2)), True, (255, 255, 255))
                r = t.get_rect()
                r.topleft = pos
                pos = (pos[0], pos[1] + 40)
                self.screen.blit(t, r)
            t = self._font.render("checkpoint: " + str(self.car.current_checkpoint), True, (255, 255, 255))
            r = t.get_rect()
            r.topleft = pos
            self.screen.blit(t, r)
