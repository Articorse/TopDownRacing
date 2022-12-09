import pygame

from data.constants import RESOLUTIONS, PHYSICS_SCREEN_SCALE
from data.files import DIR_ASSETS, DIR_SPRITES
from data.globalvars import CURRENT_RESOLUTION


class CarModel:
    def __init__(self,
                 model_name: str,
                 mass: float,
                 power: int,
                 handling: float,
                 traction: int,
                 friction: float,
                 elasticity: float,
                 sprite_filename: str):
        self.model_name = model_name
        self.mass = mass
        self.power = power
        self.handling = handling
        self.traction = traction
        self.friction = friction
        self.elasticity = elasticity
        sp = pygame.sprite.Sprite()
        image = pygame.image.load(DIR_ASSETS + DIR_SPRITES + sprite_filename).convert_alpha()
        scale = RESOLUTIONS[CURRENT_RESOLUTION][1]
        self.internal_rect_size = image.get_rect().size * PHYSICS_SCREEN_SCALE
        sp.image = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))
        sp.rect = sp.image.get_rect()
        self.sprite = sp
