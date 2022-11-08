import math
import random
import pymunk
from pygame.sprite import Sprite
from helpers.imagehelper import *
from data.constants import *
from data.enums import Direction


def steering_function(x: float, handling: float, axis_value: float):
    y = 2000
    xy = x / y
    a = 0.1 * xy
    b = 0.03 * (-math.sqrt(xy) + 1)
    return min(a, b) * handling * axis_value


class Car:
    def __init__(
            self,
            mass: float,
            power: int,
            handling: float,
            traction: int,
            size: (float, float),
            pos: (float, float),
            friction: float,
            angle: float = random.randint(0, int(round(2 * math.pi, 2) * 100)) / 100,
            color: (int, int, int, int) = (255, 0, 0, 255),
            elasticity: float = 0.1,
            sprite: Sprite = None):
        self.is_drifting = False
        self.stunned = 0
        self.size = size
        self.power = power
        self.handling = handling
        self.traction = traction
        self.handbrake = False
        self.body = pymunk.Body()
        self.body.position = pos
        self.body.angle = angle
        self.shape = pymunk.Poly(self.body, (
            (-size[0] / 2, -size[1] / 2),
            (size[0] / 2, -size[1] / 2),
            (-size[0] / 2, size[1] / 2),
            (size[0] / 2, size[1] / 2)))
        self.shape.mass = mass
        self.shape.friction = friction
        self.shape.color = color
        self.shape.elasticity = elasticity
        self.shape.collision_type = COLLTYPE_CAR
        self.body.center_of_gravity = (-size[0] * 0.4, 0)
        self.sprite = sprite
        self.sprite.rect = self.sprite.image.get_rect()
        self.sprite.rect.center = self.body.position

        self.__base_image = self.sprite.image

    def update(self):
        # get current velocity
        sideways_velocity = self.body.velocity.dot(self.body.local_to_world((0, 1)) - self.body.position).__abs__()
        forward_velocity = self.body.velocity.dot(self.body.local_to_world((1, 0)) - self.body.position).__abs__()

        # check drifting
        if sideways_velocity > self.traction:
            self.is_drifting = True
        elif not self.handbrake and forward_velocity > sideways_velocity:
            self.is_drifting = False

        # velocity vector stabilization
        if not self.is_drifting and not self.handbrake:
            if self.body.velocity.dot(self.body.local_to_world((1, 0)) - self.body.position) > 0:
                forward_vector_normalized = self.body.local_to_world((1, 0)) - self.body.position
            else:
                forward_vector_normalized = self.body.position - self.body.local_to_world((1, 0))
            new_forward_vector_normalized = (forward_vector_normalized + self.body.velocity.normalized()).normalized()
            cosine_factor = math.cos(
                self.body.velocity.angle_degrees
                - forward_vector_normalized.angle_degrees).__abs__()
            old_velocity = self.body.velocity
            self.body.velocity = new_forward_vector_normalized * old_velocity.length * cosine_factor
            self.body.velocity += old_velocity * (1 - cosine_factor)
            self.body.velocity *= GLOBAL_LINEAR_DRAG
            self.body.angular_velocity *= GLOBAL_ANGULAR_DRAG
            if self.body.velocity.length < MIN_SPEED:
                self.body.velocity *= 0
            if self.body.velocity.length > MAX_SPEED:
                self.body.velocity = self.body.velocity.normalized() * MAX_SPEED
        else:
            self.body.velocity *= GLOBAL_LINEAR_DRAG

        # stun
        if self.stunned > 0:
            self.stunned -= 1

        # update sprite
        self.sprite.rect.center = self.body.position
        rotatedImage = RotateImage(self.__base_image, self.sprite.rect.center, -math.degrees(self.body.angle))
        self.sprite.image = rotatedImage[0]
        self.sprite.rect = rotatedImage[1]

    def move(self, direction: Direction, axis_value: float):
        if not self.stunned:
            if direction == Direction.Forward:
                self.body.apply_force_at_local_point((self.power * axis_value, 0))
            if direction == Direction.Right:
                self.body.angle += steering_function(self.body.velocity.length, self.handling, axis_value)
