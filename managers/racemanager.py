import random
import time
import pygame
import pymunk
import pymunk.pygame_util
from typing import List, Optional
from pygame.font import Font
from pygame.math import Vector2
from pymunk import Vec2d
from ai.agent import Agent
from data import globalvars
from data.constants import *
from entities.car import Car
from entities.singleton import Singleton
from entities.track import Track, RaceDirection
from utils.timerutils import FormatTime
from utils.uiutils import DrawText, ImageAlign


def left_turn_collider_blocked_callback_presolve(arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict):
    for car in RaceManager().cars:
        if car.agent.left_turn_collider in arbiter.shapes:
            distance_sqrd = arbiter.contact_point_set.points[0].distance
            car.agent.left_front_collision = (False, 0)
            car.agent.left_back_collision = (False, 0)
            shapes = space.shape_query(car.agent.left_front_collider)
            for shape in shapes:
                if shape.shape.collision_type == COLLTYPE_TRACK:
                    car.agent.left_front_collision = (True, distance_sqrd)
                    break
            shapes = space.shape_query(car.agent.left_back_collider)
            for shape in shapes:
                if shape.shape.collision_type == COLLTYPE_TRACK:
                    car.agent.left_back_collision = (True, distance_sqrd)
                    break
            break
    return False


def left_turn_collider_blocked_callback_separate(arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict):
    for car in RaceManager().cars:
        if car.agent.left_turn_collider in arbiter.shapes:
            car.agent.left_front_collision = (False, 0)
            car.agent.left_back_collision = (False, 0)
            break


def right_turn_collider_blocked_callback_presolve(arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict):
    for car in RaceManager().cars:
        if car.agent.right_turn_collider in arbiter.shapes:
            distance_sqrd = arbiter.contact_point_set.points[0].distance
            car.agent.right_front_collision = (False, 0)
            car.agent.right_back_collision = (False, 0)
            shapes = space.shape_query(car.agent.right_front_collider)
            for shape in shapes:
                if shape.shape.collision_type == COLLTYPE_TRACK:
                    car.agent.right_front_collision = (True, distance_sqrd)
                    break
            shapes = space.shape_query(car.agent.right_back_collider)
            for shape in shapes:
                if shape.shape.collision_type == COLLTYPE_TRACK:
                    car.agent.right_back_collision = (True, distance_sqrd)
                    break
            break
    return False


def right_turn_collider_blocked_callback_separate(arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict):
    for car in RaceManager().cars:
        if car.agent.right_turn_collider in arbiter.shapes:
            car.agent.right_front_collision = (False, 0)
            car.agent.right_back_collision = (False, 0)
            break


def car_track_collision_callback(arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict):
    if arbiter.is_first_contact and arbiter.total_impulse.length > CAR_STUN_MIN_IMPULSE:
        for car in RaceManager().cars:
            if car.shape in arbiter.shapes:
                car.stunned = CAR_STUN_DURATION * FPS
                break


def checkpoint_reached_callback(arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict):
    agent: Optional[Agent] = None
    car_shape: Optional[pymunk.Shape] = None
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
    current_checkpoint = RaceManager().track.checkpoints[agent.current_checkpoint]
    if current_checkpoint[0] == checkpoint_shape.a and current_checkpoint[1] == checkpoint_shape.b:
        RaceManager().UpdateLeaderboard(agent.car, agent.current_checkpoint)
        if agent.car.lap == RaceManager().laps and agent.current_checkpoint == 0:
            agent.is_enabled = True
            agent.car.has_finished = True
            if not RaceManager().is_over:
                for car in RaceManager().cars:
                    RaceManager().final_lineup[car] = INT_MAX_VALUE
            RaceManager().is_over = True
            RaceManager().final_lineup[agent.car] = RaceManager().GetTime()
            RaceManager().final_lineup = dict(sorted(RaceManager().final_lineup.items(), key=lambda item: item[1]))
        if agent.current_checkpoint < len(RaceManager().track.checkpoints) - 1:
            agent.current_checkpoint += 1
            return True
        else:
            agent.current_checkpoint = 0
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
        self.Free()

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
        self.laps = DEFAULT_LAPS
        self.is_initialized = False
        self.is_started = False
        self.is_over = False
        self.final_lineup: {Car, float} = {}
        self.player_car: Optional[Car] = None
        self.countdown_time: float = RACE_COUNTDOWN
        self.background: Optional[pygame.sprite.Sprite] = None

    def SetTrack(self, track: Track, space: pymunk.Space):
        self.track = track
        self.track.AddToSpace(space)

    def AddCars(self, space: pymunk.Space, *cars: Car):
        for i in range(len(cars)):
            RaceManager().cars.append(cars[i])
            space.add(RaceManager().cars[i].body, RaceManager().cars[i].shape)
            RaceManager().cars[i].agent = Agent(space, RaceManager().cars[i], RaceManager().track)
            RaceManager().agents.append(RaceManager().cars[i].agent)
            if self.track.direction == RaceDirection.Up:
                pos_x = self.track.start_position.x
                pos_y = self.track.start_position.y + CAR_SEPARATION.y * i
                if i % 2 == 1:
                    pos_x -= CAR_SEPARATION.x
                RaceManager().cars[i].body.position = Vec2d(pos_x, pos_y)
                RaceManager().cars[i].body.angle = UP_ANGLE
            elif self.track.direction == RaceDirection.Right:
                pos_x = self.track.start_position.x + CAR_SEPARATION.x * i
                pos_y = self.track.start_position.y
                if i % 2 == 1:
                    pos_y += CAR_SEPARATION.y
                RaceManager().cars[i].body.position = Vec2d(pos_x, pos_y)
                RaceManager().cars[i].body.angle = RIGHT_ANGLE
            elif self.track.direction == RaceDirection.Down:
                pos_x = self.track.start_position.x
                pos_y = self.track.start_position.y - CAR_SEPARATION.y * i
                if i % 2 == 1:
                    pos_x += CAR_SEPARATION.x
                RaceManager().cars[i].body.position = Vec2d(pos_x, pos_y)
                RaceManager().cars[i].body.angle = DOWN_ANGLE
            else:
                pos_x = self.track.start_position.x - CAR_SEPARATION.x * i
                pos_y = self.track.start_position.y
                if i % 2 == 1:
                    pos_y -= CAR_SEPARATION.y
                RaceManager().cars[i].body.position = Vec2d(pos_x, pos_y)
                RaceManager().cars[i].body.angle = LEFT_ANGLE

    def UpdateLeaderboard(self, car: Car, checkpoint: int):
        if checkpoint == 0:
            car.lap += 1
        self.leaderboard.append(_LeaderboardEntry(car, checkpoint, car.lap, self.GetTime()))
        self.leaderboard.sort(key=lambda x: x.time)

    def GetTime(self):
        return int((time.perf_counter() - self.start_time) * 1000)

    def Setup(self, track: Track, player_car: Car, laps: int, *cars: Car):
        # pymunk initialization
        self.space = pymunk.Space()
        self.space.collision_bias = 0
        self.space.iterations = 30
        self.pymunk_screen = pygame.Surface(track.size)
        self.pymunk_screen.set_colorkey((12, 12, 12))
        self.pymunk_screen.fill((12, 12, 12))
        self.draw_options = pymunk.pygame_util.DrawOptions(self.pymunk_screen)
        self.space.add_collision_handler(COLLTYPE_CAR, COLLTYPE_TRACK).post_solve = car_track_collision_callback
        self.space.add_collision_handler(COLLTYPE_CAR, COLLTYPE_CHECKPOINT).pre_solve = checkpoint_reached_callback
        self.space.add_collision_handler(
            COLLTYPE_LEFT_TURN_COLLIDER, COLLTYPE_TRACK).pre_solve = left_turn_collider_blocked_callback_presolve
        self.space.add_collision_handler(
            COLLTYPE_LEFT_TURN_COLLIDER, COLLTYPE_TRACK).separate = left_turn_collider_blocked_callback_separate
        self.space.add_collision_handler(
            COLLTYPE_RIGHT_TURN_COLLIDER, COLLTYPE_TRACK).pre_solve = right_turn_collider_blocked_callback_presolve
        self.space.add_collision_handler(
            COLLTYPE_RIGHT_TURN_COLLIDER, COLLTYPE_TRACK).separate = right_turn_collider_blocked_callback_separate

        # load track
        self.SetTrack(track, self.space)
        self.laps = laps

        # add cars
        self.AddCars(self.space, *cars)
        self.player_car = player_car

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

        # DEBUG START
        if globalvars.ENVIRONMENT_DEBUG:
            # setup background
            self.background = pygame.sprite.Sprite()
            bg_image = pygame.Surface(track.size)
            bg_image.fill((30, 30, 30))
            for _ in range(2000):
                bg_x, bg_y = random.randint(0, track.size.x), random.randint(0, track.size.y)
                pygame.draw.rect(bg_image, pygame.Color('gray'), (bg_x, bg_y, 2, 2))
            self.background.image = bg_image
            self.background.rect = bg_image.get_rect()
        # DEBUG END
        if not globalvars.ENVIRONMENT_DEBUG:
            self.background = track.background_filename

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
                        screen, font, pos, ImageAlign.TOP_RIGHT)
                    pos = (pos[0], pos[1] + 40)
