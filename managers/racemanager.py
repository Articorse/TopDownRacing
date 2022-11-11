from operator import itemgetter
from typing import List

import pygame
import pymunk
from pygame.font import Font
from pymunk import Vec2d

from ai.agent import Agent
from data.constants import SCREEN_SIZE, CAR_SEPARATION
from entities.car import Car
from entities.singleton import Singleton
from entities.track import Track
from helpers.timerhelper import FormatTime


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
        self.track = None
        self.current_time: int = 0
        self.leaderboard: List[_LeaderboardEntry] = []

    def SetTrack(self, track: {}, space: pymunk.Space):
        self.track = Track(**track)
        self.track.AddToSpace(space)

    def AddCars(self, cars: List[tuple[str, {}]], space: pymunk.Space):
        for i in range(len(cars)):
            RaceManager().cars.append(Car(cars[i][0], **cars[i][1]))
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
        self.leaderboard.append(_LeaderboardEntry(car, checkpoint, car.lap, self.current_time))
        self.leaderboard.sort(key=lambda x: x.time)

    def DebugDrawInfo(self, screen: pygame.Surface, font: Font, cars: List[Car]):
        if screen and font:
            pos = (SCREEN_SIZE.x - 20, 20)
            for entry in self.leaderboard:
                if entry.car in cars:
                    t = font.render(entry.car.name + " " + str(entry.lap) + " " + str(entry.checkpoint) + " " + str(FormatTime(entry.time)), True, (255, 255, 255))
                    r = t.get_rect()
                    r.topright = pos
                    pos = (pos[0], pos[1] + 40)
                    screen.blit(t, r)
