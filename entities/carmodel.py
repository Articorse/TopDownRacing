import pygame

from data.constants import CAR_SCALE
from data.files import ASSETS_DIR, SPRITES_DIR


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
        image = pygame.image.load(ASSETS_DIR + SPRITES_DIR + sprite_filename).convert_alpha()
        sp.image = pygame.transform.scale(image, (image.get_width() * CAR_SCALE, image.get_height() * CAR_SCALE))
        sp.rect = sp.image.get_rect()
        self.sprite = sp
