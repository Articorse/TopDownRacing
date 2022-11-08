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


class InputHelper:
    def __init__(self, joystick: pygame.joystick):
        self.joystick = joystick
        self.__default_inputs = {
            "forward": 0.0,
            "right": 0.0,
            "handbrake": False,
            "quit": False
        }
        self.__inputs = self.__default_inputs.copy()

    def __reset_inputs(self):
        self.__inputs["forward"] = self.__default_inputs["forward"]
        self.__inputs["right"] = self.__default_inputs["right"]
        self.__inputs["handbrake"] = self.__default_inputs["handbrake"]
        self.__inputs["quit"] = self.__default_inputs["quit"]
    
    def get_inputs(self, events: list[Event]):
        self.__reset_inputs()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.__inputs["quit"] = True

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_w]:
            self.__inputs["forward"] = 1.0
        if pressed_keys[pygame.K_s]:
            self.__inputs["forward"] = -1.0
        if pressed_keys[pygame.K_a]:
            self.__inputs["right"] = -1.0
        if pressed_keys[pygame.K_d]:
            self.__inputs["right"] = 1.0
        if pressed_keys[pygame.K_SPACE]:
            self.__inputs["handbrake"] = True
    
        if self.__inputs["forward"] == 0:
            self.__inputs["forward"] = (self.joystick.get_axis(5) + 1) / 2 + -(self.joystick.get_axis(4) + 1) / 2
        if self.__inputs["right"] == 0:
            self.__inputs["right"] = self.joystick.get_axis(0)
        if not self.__inputs["handbrake"]:
            self.__inputs["handbrake"] = self.joystick.get_button(0)

        return self.__inputs
            