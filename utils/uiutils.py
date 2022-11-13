from enum import Enum

import pygame
from pygame.font import Font


class TextAlign(Enum):
    TOP_LEFT = 0
    TOP_RIGHT = 1
    CENTER = 2


def DrawText(
        text: str,
        surface: pygame.Surface,
        font: Font,
        pos: (int, int),
        align: TextAlign = TextAlign.TOP_LEFT,
        scale: float = 1,
        color: (int, int, int) = (255, 255, 255)):
    text_image = font.render(text, True, color)
    width = text_image.get_width()
    height = text_image.get_height()
    text_image = pygame.transform.scale(text_image, (int(width * scale), int(height * scale)))
    text_rect = text_image.get_rect()
    if align == TextAlign.TOP_LEFT:
        text_rect.topleft = pos
    elif align == TextAlign.TOP_RIGHT:
        text_rect.topright = pos
    elif align == TextAlign.CENTER:
        text_rect.center = pos
    surface.blit(text_image, text_rect)


class Button:
    def __init__(self,
                 text: str,
                 font: Font,
                 pos: (int, int),
                 scale: float = 1,
                 align: TextAlign = TextAlign.TOP_LEFT,
                 color: (int, int, int) = (255, 255, 255)):
        text_image = font.render(text, True, color)
        width = text_image.get_width()
        height = text_image.get_height()
        self.image = pygame.transform.scale(text_image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        if align == TextAlign.TOP_LEFT:
            self.rect.topleft = pos
        elif align == TextAlign.TOP_RIGHT:
            self.rect.topright = pos
        elif align == TextAlign.CENTER:
            self.rect.center = pos
        self.clicked = False

    def Draw(self, surface: pygame.Surface):
        action = False
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                action = True

        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        surface.blit(self.image, self.rect)

        return action
