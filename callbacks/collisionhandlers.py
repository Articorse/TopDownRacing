import pymunk

from ai.agent import Agent
from data.constants import *
from managers.racemanager import RaceManager


def car_track_collision_callback(arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict):
    if arbiter.is_first_contact and arbiter.total_impulse.length > CAR_STUN_MIN_IMPULSE:
        for car in RaceManager().cars:
            if car.shape in arbiter.shapes:
                car.stunned = CAR_STUN_DURATION * FPS
                break


def checkpoint_reached_callback(arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict):
    agent: Agent
    car_shape: pymunk.Shape
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
    current_guidepoint = RaceManager().track.guidepoints[agent.current_guidepoint]
    if current_guidepoint[0] == checkpoint_shape.a and current_guidepoint[1] == checkpoint_shape.b:
        if agent.current_guidepoint in RaceManager().track.checkpoints:
            checkpoint = RaceManager().track.checkpoints.index(agent.current_guidepoint)
            RaceManager().UpdateLeaderboard(agent.car, checkpoint)
        if agent.current_guidepoint < len(RaceManager().track.guidepoints) - 1:
            agent.current_guidepoint += 1
            return True
        else:
            agent.current_guidepoint = 0
            return True
    return False
