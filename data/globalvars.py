from typing import Optional

import pygame

from data.constants import FPS_UPDATE_TIMER_DEFAULT, FPS

ENVIRONMENT_DEBUG = False
LAST_FRAME_TIME = 0
FPS_REFRESH_TIMER = FPS_UPDATE_TIMER_DEFAULT
CURRENT_FPS = FPS
RECENT_FPS_VALUES = []
CURRENT_RESOLUTION = 1  # Replace with options.json
CURRENT_WINDOWED = pygame.NOEVENT  # Replace with options.json
SCREEN: Optional[pygame.Surface] = None
