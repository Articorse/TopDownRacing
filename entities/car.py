import math
import pymunk
from pymunk import Vec2d

from entities.carmodel import CarModel
from utils.imageutils import *
from data.constants import *
from data.enums import Direction


def _SteeringFunction(x: float, handling: float, axis_value: float):
    y = 2000
    xy = x / y
    a = 0.1 * xy
    b = 0.03 * (-math.sqrt(xy) + 1)
    return min(a, b) * handling * axis_value


class Car:
    def __init__(
            self,
            name: str,
            car_model: CarModel):
        self.name = name
        self.car_model = car_model
        self.is_drifting = False
        self.stunned = 0
        self.lap = 0
        self.model_name = car_model.model_name
        self.has_finished = False
        self.handbrake = False
        self.agent = None
        self.body = pymunk.Body()
        self.body.position = Vec2d(0, 0)
        self.body.angle = 0
        self.shape = pymunk.Poly(self.body, (
            (-car_model.size[0] / 2, -car_model.size[1] / 2),
            (car_model.size[0] / 2, -car_model.size[1] / 2),
            (-car_model.size[0] / 2, car_model.size[1] / 2),
            (car_model.size[0] / 2, car_model.size[1] / 2)))
        self.shape.mass = car_model.mass
        self.shape.friction = car_model.friction
        self.shape.color = (12, 12, 12, 12)
        self.shape.elasticity = car_model.elasticity
        self.shape.collision_type = COLLTYPE_CAR
        self.shape.filter = pymunk.ShapeFilter(categories=SF_CAR)
        self.body.center_of_gravity = (-car_model.size[0] * 0.4, 0)
        sp = pygame.sprite.Sprite()
        sp.image = pygame.image.load(car_model.sprite_path)
        sp.image = pygame.transform.scale(sp.image, (60, 40)).convert_alpha()
        sp.rect = sp.image.get_rect()
        sp.rect.center = self.body.position
        self.sprite = sp
        self.facing_vector = Vec2d(1, 0).rotated(self.body.angle)

        self.__base_image = self.sprite.image

    def Update(self):
        # get current velocity
        sideways_velocity = self.body.velocity.dot(self.body.local_to_world((0, 1)) - self.body.position).__abs__()
        forward_velocity = self.body.velocity.dot(self.body.local_to_world((1, 0)) - self.body.position).__abs__()
        self.facing_vector = Vec2d(1, 0).rotated(self.body.angle)

        # check drifting
        if sideways_velocity > self.car_model.traction:
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
            if not self.is_drifting:
                self.body.velocity *= GLOBAL_LINEAR_DRAG
            else:
                self.body.velocity *= GLOBAL_DRIFT_DRAG
            self.body.angular_velocity *= GLOBAL_ANGULAR_DRAG
            if self.body.velocity.length < MIN_SPEED:
                self.body.velocity *= 0
        else:
            if not self.is_drifting:
                self.body.velocity *= GLOBAL_LINEAR_DRAG
            else:
                self.body.velocity *= GLOBAL_DRIFT_DRAG

        # stun
        if self.stunned > 0:
            self.is_drifting = True
            self.stunned -= 1

        # update sprite
        self.sprite.rect.center = self.body.position
        rotatedImage = RotateImage(self.__base_image, self.sprite.rect.center, -math.degrees(self.body.angle))
        self.sprite.image = rotatedImage[0]
        self.sprite.rect = rotatedImage[1]

    def Move(self, direction: Direction, axis_value: float):
        if not self.stunned:
            if direction == Direction.Forward:
                self.body.apply_force_at_local_point((self.car_model.power * axis_value, 0))
            if direction == Direction.Right:
                if self.body.velocity.dot(self.body.local_to_world((1, 0)) - self.body.position) > 0:
                    self.body.angle += _SteeringFunction(self.body.velocity.length, self.car_model.handling, axis_value)
                else:
                    self.body.angle -= _SteeringFunction(self.body.velocity.length, self.car_model.handling, axis_value)
