from typing import Optional

import pygame

from data.constants import FPS_UPDATE_TIMER_DEFAULT, FPS, AUDIO_ENGINE_NOISE_TIMER

ENVIRONMENT_DEBUG = False
LAST_FRAME_TIME = 0
FPS_REFRESH_TIMER = FPS_UPDATE_TIMER_DEFAULT
ENGINE_NOISE_REFRESH_TIMER = AUDIO_ENGINE_NOISE_TIMER
CURRENT_FPS = FPS
RECENT_FPS_VALUES = []
CURRENT_RESOLUTION = 1  # Replace with options.json
CURRENT_WINDOWED = pygame.NOEVENT  # Replace with options.json
SCREEN: Optional[pygame.Surface] = None
MUSIC_VOLUME = 1  # Replace with options.json
SFX_VOLUME = 1  # Replace with options.json
UI_VOLUME = 1  # Replace with options.json
RACE_MANAGER = None
