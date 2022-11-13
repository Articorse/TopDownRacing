import time
import pygame
import pymunk
import pymunk.pygame_util
from typing import List, Optional
from pygame.font import Font
from pygame.math import Vector2
from pymunk import Vec2d
from ai.agent import Agent
from data.constants import *
from entities.car import Car
from entities.singleton import Singleton
from entities.track import Track
from utils.timerutils import FormatTime
from utils.uiutils import DrawText, TextAlign


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
            if agent.car.lap == LAPS_TO_WIN and agent.current_guidepoint == 0:
                agent.is_enabled = True
                agent.car.has_finished = True
                if not RaceManager().is_over:
                    for car in RaceManager().cars:
                        RaceManager().final_lineup[car] = INT_MAX_VALUE
                RaceManager().is_over = True
                RaceManager().final_lineup[agent.car] = RaceManager().GetTime()
                RaceManager().final_lineup = dict(sorted(RaceManager().final_lineup.items(), key=lambda item: item[1]))
        if agent.current_guidepoint < len(RaceManager().track.guidepoints) - 1:
            agent.current_guidepoint += 1
            return True
        else:
            agent.current_guidepoint = 0
            return True
    return False


class _LeaderboardEntry:
    def __init__(self, car: Car, checkpoint: int, lap: int, time: int):
        self.car = car
        self.checkpoint = checkpoint
        self.lap = lap
        self.time = time


class RaceManager(metaclass=Singleton):
    def __init__(self):
        self.cars: List[Car] = []
        self.agents: List[Agent] = []
        self.track: Optional[Track] = None
        self.start_time: float = 0
        self.leaderboard: List[_LeaderboardEntry] = []
        self.space: Optional[pymunk.Space] = None
        self.pymunk_screen: Optional[pygame.Surface] = None
        self.draw_options: Optional[pymunk.pygame_util.DrawOptions] = None
        self.camera = Vector2(0, 0)
        self.sprites: Optional[pygame.sprite.Group] = None
        self.is_initialized = False
        self.is_started = False
        self.is_over = False
        self.final_lineup: {Car, float} = {}
        self.player_car: Optional[Car] = None
        self.countdown_time: float = RACE_COUNTDOWN

    def Free(self):
        self.cars: List[Car] = []
        self.agents: List[Agent] = []
        self.track: Optional[Track] = None
        self.start_time: float = 0
        self.leaderboard: List[_LeaderboardEntry] = []
        self.space: Optional[pymunk.Space] = None
        self.pymunk_screen: Optional[pygame.Surface] = None
        self.draw_options: Optional[pymunk.pygame_util.DrawOptions] = None
        self.camera = Vector2(0, 0)
        self.sprites: Optional[pygame.sprite.Group] = None
        self.is_initialized = False
        self.is_started = False
        self.is_over = False
        self.final_lineup: {Car, float} = {}
        self.player_car: Optional[Car] = None
        self.countdown_time: float = RACE_COUNTDOWN

    def SetTrack(self, track: Track, space: pymunk.Space):
        self.track = track
        self.track.AddToSpace(space)

    def AddCars(self, space: pymunk.Space, *cars: Car):
        for i in range(len(cars)):
            RaceManager().cars.append(cars[i])
            RaceManager().cars[i].agent = Agent(space, RaceManager().cars[i])
            RaceManager().agents.append(RaceManager().cars[i].agent)
            space.add(RaceManager().cars[i].body, RaceManager().cars[i].shape)
            # TODO: Account for tracks that begin in different orientations.
            pos_x = self.track.start_position.pos.x - CAR_SEPARATION.x * i
            pos_y = self.track.start_position.pos.y
            if i % 2 == 1:
                pos_y += CAR_SEPARATION.y
            RaceManager().cars[i].body.position = Vec2d(pos_x, pos_y)
            RaceManager().cars[i].body.angle = self.track.start_position.angle

    def UpdateLeaderboard(self, car: Car, checkpoint: int):
        if checkpoint == 0:
            car.lap += 1
        self.leaderboard.append(_LeaderboardEntry(car, checkpoint, car.lap, self.GetTime()))
        self.leaderboard.sort(key=lambda x: x.time)

    def GetTime(self):
        return int((time.perf_counter() - self.start_time) * 1000)

    def SetupRace(self, track: Track, cars: List[Car], player_car_index: int):
        # pymunk initialization
        self.space = pymunk.Space()
        self.space.collision_bias = 0
        self.space.iterations = 30
        self.pymunk_screen = pygame.Surface(track.size)
        self.pymunk_screen.set_colorkey((12, 12, 12))
        self.pymunk_screen.fill((12, 12, 12))
        self.draw_options = pymunk.pygame_util.DrawOptions(self.pymunk_screen)
        self.space.add_collision_handler(COLLTYPE_CAR, COLLTYPE_TRACK).post_solve = car_track_collision_callback
        self.space.add_collision_handler(COLLTYPE_CAR, COLLTYPE_GUIDEPOINT).begin = checkpoint_reached_callback

        # load track
        self.SetTrack(track, self.space)

        # add cars
        self.AddCars(self.space, *cars)
        self.player_car = self.cars[player_car_index]

        # camera initialization
        self.camera = pygame.Vector2(
            -self.player_car.body.position.x,
            -self.player_car.body.position.y) + SCREEN_SIZE / 2

        # add sprites to group
        self.sprites = pygame.sprite.Group()
        for car in self.cars:
            self.sprites.add(car.sprite)

        self.countdown_time = RACE_COUNTDOWN
        self.start_time = time.perf_counter()
        self.is_initialized = True

    def StartRace(self):
        self.start_time = time.perf_counter()
        self.is_started = True

    def DebugDrawInfo(self, screen: pygame.Surface, font: Font, *cars: Car):
        if screen and font:
            pos = (SCREEN_SIZE.x - 20, 20)
            for entry in self.leaderboard:
                if entry.car in cars:
                    DrawText(
                        entry.car.name + " " +
                        str(entry.lap) + " " +
                        str(entry.checkpoint) + " " +
                        str(FormatTime(entry.time)),
                        screen, font, pos, TextAlign.TOP_RIGHT)
                    pos = (pos[0], pos[1] + 40)
