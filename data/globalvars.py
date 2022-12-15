from typing import Optional

import pygame

from data.constants import FPS

ENVIRONMENT_DEBUG = False
LAST_FRAME_TIME = 0
CURRENT_FPS = FPS
RECENT_FPS_VALUES = []
CURRENT_RESOLUTION = 2  # Replace with options.json
CURRENT_WINDOWED = pygame.NOFRAME  # Replace with options.json
SCREEN: Optional[pygame.Surface] = None
MUSIC_VOLUME = 1  # Replace with options.json
SFX_VOLUME = 1  # Replace with options.json
UI_VOLUME = 1  # Replace with options.json
RACE_MANAGER = None
