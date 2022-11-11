from typing import List

from ai.agent import Agent
from entities.car import Car
from entities.singleton import Singleton
from entities.track import Track


class RaceManager(metaclass=Singleton):
    def __init__(self):
        self.cars: List[Car] = []
        self.agents: List[Agent] = []
        self.track: Track
        self.current_time: int = 0
