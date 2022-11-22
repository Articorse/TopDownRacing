# INPUT MAPPING
# Axes:
# 0 - Left Analog Horizontal
# 1 - Left Analog Vertical
# 2 - Right Analog Horizontal
# 3 - Right Analog Vertical
# Buttons:
# 0 - A
# 1 - B
# 2 - X
# 3 - Y
# 4 - LB
# 5 - RB
# 6 - Back
# 7 - Start
# 8 - Left Analog
# 9 - Right Analog

import pygame
from pygame.event import Event

from data import globalvars
from data.constants import INPUT_FORWARD, INPUT_RIGHT, INPUT_HANDBRAKE, INPUT_QUIT, INPUT_DEBUG_TOGGLE
from entities.singleton import Singleton


class InputManager(metaclass=Singleton):
    def __init__(self, joystick: pygame.joystick = None):
        self.joystick = joystick
        self.__default_inputs = {
            INPUT_FORWARD: 0.0,
            INPUT_RIGHT: 0.0,
            INPUT_HANDBRAKE: False,
            INPUT_QUIT: False,
            INPUT_DEBUG_TOGGLE: False
        }
        self.__reset_inputs()

    def __reset_inputs(self):
        self.__inputs = self.__default_inputs.copy()
    
    def get_inputs(self, events: list[Event]):
        self.__reset_inputs()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.__inputs[INPUT_QUIT] = True
                if event.key == pygame.K_TAB:
                    globalvars.ENVIRONMENT_DEBUG = not globalvars.ENVIRONMENT_DEBUG

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_w]:
            self.__inputs[INPUT_FORWARD] = 1.0
        if pressed_keys[pygame.K_s]:
            self.__inputs[INPUT_FORWARD] = -1.0
        if pressed_keys[pygame.K_a]:
            self.__inputs[INPUT_RIGHT] = -1.0
        if pressed_keys[pygame.K_d]:
            self.__inputs[INPUT_RIGHT] = 1.0
        if pressed_keys[pygame.K_SPACE]:
            self.__inputs[INPUT_HANDBRAKE] = True

        if self.joystick:
            if self.__inputs[INPUT_FORWARD] == 0:
                self.__inputs[INPUT_FORWARD] = (self.joystick.get_axis(5) + 1) / 2 +\
                                               -(self.joystick.get_axis(4) + 1) / 2
            if self.__inputs[INPUT_RIGHT] == 0:
                self.__inputs[INPUT_RIGHT] = self.joystick.get_axis(0)
            if not self.__inputs[INPUT_HANDBRAKE]:
                self.__inputs[INPUT_HANDBRAKE] = self.joystick.get_button(0)

        return self.__inputs
            