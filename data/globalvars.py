from typing import Optional

import pygame

from data.constants import FPS

ENVIRONMENT_DEBUG = False
LAST_FRAME_TIME = 0
CURRENT_FPS = FPS
RECENT_FPS_VALUES = []
SCREEN: Optional[pygame.Surface] = None
RACE_MANAGER = None
