import pymunk
from data.constants import *
from data.globals import cars


def car_track_collision_callback(arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict):
    if arbiter.is_first_contact and arbiter.total_impulse.length > CAR_STUN_MIN_IMPULSE:
        for car in cars:
            if car.shape in arbiter.shapes:
                car.stunned = CAR_STUN_DURATION * FPS
                break
