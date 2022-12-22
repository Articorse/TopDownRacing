import json
import os.path
from os.path import isfile

import pygame

from data.files import FILE_OPTIONS, DIR_OPTIONS


def _IsValid(j: dict):
    if "current_resolution" not in j.keys():
        return False
    elif type(j["current_resolution"]) is not int:
        return False

    if "current_windowed" not in j.keys():
        return False
    elif type(j["current_windowed"]) is not int or j["current_windowed"] not in [pygame.NOEVENT, pygame.NOFRAME]:
        return False

    if "music_volume" not in j.keys():
        return False
    elif type(j["music_volume"]) not in [float, int]:
        return False

    if "sfx_volume" not in j.keys():
        return False
    elif type(j["sfx_volume"]) not in [float, int]:
        return False

    if "ui_volume" not in j.keys():
        return False
    elif type(j["ui_volume"]) not in [float, int]:
        return False

    return True


class Options:
    def __init__(self):
        self.current_resolution = 2
        self.current_windowed = pygame.NOFRAME
        self.music_volume = 1.0
        self.sfx_volume = 1.0
        self.ui_volume = 1.0

    def Save(self):
        if not os.path.exists(DIR_OPTIONS):
            os.makedirs(DIR_OPTIONS)
        with open(FILE_OPTIONS, 'w') as outfile:
            json.dump(self.__dict__, outfile, indent=4)

    def Load(self):
        if isfile(FILE_OPTIONS):
            loaded_options = json.load(open(FILE_OPTIONS))
            if _IsValid(loaded_options):
                self.current_resolution = loaded_options["current_resolution"]
                self.current_windowed = loaded_options["current_windowed"]
                self.music_volume = loaded_options["music_volume"]
                self.sfx_volume = loaded_options["sfx_volume"]
                self.ui_volume = loaded_options["ui_volume"]

    def Copy(self):
        new_options = Options()
        new_options.current_resolution = self.current_resolution
        new_options.current_windowed = self.current_windowed
        new_options.music_volume = self.music_volume
        new_options.sfx_volume = self.sfx_volume
        new_options.ui_volume = self.ui_volume
        return new_options
