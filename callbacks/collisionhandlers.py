import pymunk
from data.constants import *
from managers.racemanager import RaceManager


def car_track_collision_callback(arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict):
    if arbiter.is_first_contact and arbiter.total_impulse.length > CAR_STUN_MIN_IMPULSE:
        for car in RaceManager().cars:
            if car.shape in arbiter.shapes:
                car.stunned = CAR_STUN_DURATION * FPS
                break


def checkpoint_reached_callback(arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict):
    agent = None
    car_shape = None
    for car in RaceManager().cars:
        if car.shape in arbiter.shapes:
            car_shape = car.shape
            agent = car.agent
            break
    if not agent or not car_shape:
        return False
    checkpoint_shape = None
    for shape in arbiter.shapes:
        if shape is not car_shape:
            checkpoint_shape = shape
            break
    current_checkpoint = RaceManager().track.checkpoint_data[agent.car.current_checkpoint]
    if current_checkpoint[0] == checkpoint_shape.a and current_checkpoint[1] == checkpoint_shape.b:
        if agent.car.current_checkpoint < len(RaceManager().track.checkpoint_data) - 1:
            agent.car.current_checkpoint += 1
            return True
        else:
            agent.car.current_checkpoint = 0
            return True
    return False
