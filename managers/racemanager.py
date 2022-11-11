from operator import itemgetter
from typing import List

import pygame
from pygame.font import Font

from ai.agent import Agent
from data.constants import SCREEN_SIZE
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
        self.track: Track
        self.current_time: int = 0
        self.leaderboard: List[_LeaderboardEntry] = []

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
