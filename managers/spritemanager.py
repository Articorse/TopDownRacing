import pygame

from data.constants import UI_DYNAMIC_BUTTON, UI_NORMAL, UI_HOVER, UI_CLICK, UI_LEFT, UI_MIDDLE, UI_RIGHT, \
    UI_DYNAMIC_BUTTON_ALT
from data.files import DIR_UI, UI_ELEMENT_DICT
from entities.singleton import Singleton
from enums.imagealign import ImageAlign


class SpriteManager(metaclass=Singleton):
    def __init__(self):
        self.button_sprites: dict[str, dict[str, dict[str, pygame.Surface]]] = {
            UI_DYNAMIC_BUTTON: {
                UI_NORMAL: {UI_LEFT: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON][0][0]),
                            UI_MIDDLE: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON][0][1]),
                            UI_RIGHT: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON][0][2])},
                UI_HOVER: {UI_LEFT: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON][1][0]),
                           UI_MIDDLE: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON][1][1]),
                           UI_RIGHT: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON][1][2])},
                UI_CLICK: {UI_LEFT: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON][2][0]),
                           UI_MIDDLE: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON][2][1]),
                           UI_RIGHT: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON][2][2])}},
            UI_DYNAMIC_BUTTON_ALT: {
                UI_NORMAL: {UI_LEFT: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON_ALT][0][0]),
                            UI_MIDDLE: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON_ALT][0][1]),
                            UI_RIGHT: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON_ALT][0][2])},
                UI_HOVER: {UI_LEFT: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON_ALT][1][0]),
                           UI_MIDDLE: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON_ALT][1][1]),
                           UI_RIGHT: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON_ALT][1][2])},
                UI_CLICK: {UI_LEFT: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON_ALT][2][0]),
                           UI_MIDDLE: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON_ALT][2][1]),
                           UI_RIGHT: pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON_ALT][2][2])}}
            }

        self.button_decals: dict[str, [dict[str, tuple[pygame.Surface, ImageAlign, tuple[int, int]]]]] = {
            UI_DYNAMIC_BUTTON: {
                UI_NORMAL: (
                    pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON][3]), ImageAlign.TOP_RIGHT, (-40, 5)),
                UI_HOVER: (
                    pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON][3]), ImageAlign.TOP_RIGHT, (-40, 5)),
                UI_CLICK: (
                    pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON][3]), ImageAlign.TOP_RIGHT, (-20, 5))},
            UI_DYNAMIC_BUTTON_ALT: {
                UI_NORMAL: (
                    pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON][3]), ImageAlign.TOP_RIGHT, (-40, 5)),
                UI_HOVER: (
                    pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON][3]), ImageAlign.TOP_RIGHT, (-40, 5)),
                UI_CLICK: (
                    pygame.image.load(DIR_UI + UI_ELEMENT_DICT[UI_DYNAMIC_BUTTON][3]), ImageAlign.TOP_RIGHT, (-20, 5))}
        }
