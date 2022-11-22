import pygame

from data.files import ASSETS_DIR, SPRITES_DIR


class CarModel:
    def __init__(self,
                 model_name: str,
                 mass: float,
                 power: int,
                 handling: float,
                 traction: int,
                 size: (float, float),
                 friction: float,
                 elasticity: float,
                 sprite_filename: str):
        self.model_name = model_name
        self.mass = mass
        self.power = power
        self.handling = handling
        self.traction = traction
        self.size = size
        self.friction = friction
        self.elasticity = elasticity
        sp = pygame.sprite.Sprite()
        sp.image = pygame.image.load(ASSETS_DIR + SPRITES_DIR + sprite_filename).convert_alpha()
        sp.rect = sp.image.get_rect()
        self.sprite_path = sp
