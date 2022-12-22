import os

import pygame

from data import globalvars
from data.constants import RESOLUTIONS
from data.options import Options
from entities.singleton import Singleton
from enums.state import State


class GameManager(metaclass=Singleton):
    def __init__(self):
        self._state = State.Main_Menu
        self._options: Options = Options()
        self._options.Load()
        self.main_menu = None
        self.race_selection_menu = None
        self.options_menu = None
        self.race = None

    def GetState(self):
        return self._state

    def GetOptions(self):
        return self._options

    def SetOptions(self, new_options: Options):
        self._options = new_options

    def GetResolution(self):
        return RESOLUTIONS[self._options.current_resolution][0]

    def GetResolutionScale(self):
        return RESOLUTIONS[self._options.current_resolution][1]

    def SetResolution(self, res_index: int):
        if res_index < len(RESOLUTIONS):
            self._options.current_resolution = res_index
            res = RESOLUTIONS[res_index][0]
            os.environ['SDL_VIDEO_CENTERED'] = '1'
            globalvars.SCREEN = pygame.display.set_mode(res, GameManager().GetOptions().current_windowed)

    def SetBorder(self, bordered: bool):
        if bordered:
            bordered_flag = pygame.NOEVENT
        else:
            bordered_flag = pygame.NOFRAME
        globalvars.SCREEN = pygame.display.set_mode(GameManager().GetResolution(), bordered_flag)

    def GetBorder(self):
        if self._options.current_windowed == pygame.NOEVENT:
            return True
        else:
            return False

    def SetState(self, state: State):
        if self._state == State.Main_Menu:
            if state == State.Options:
                self._state = state
            if state == State.Selection_Screen:
                self._state = state

        if self._state == State.Options:
            if state == State.Main_Menu:
                self._state = state

        if self._state == State.Selection_Screen:
            if state == State.Main_Menu:
                self._state = state
            if state == State.In_Race:
                self._state = state

        if self._state == State.In_Race:
            if state == State.Main_Menu:
                globalvars.RaceManager = None
                self._state = state
