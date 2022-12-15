import pygame
from pygame.font import Font

from data.constants import AUDIO_CLICK, RESOLUTIONS, UI_NORMAL, UI_LEFT, UI_MIDDLE, UI_RIGHT, UI_HOVER, UI_CLICK
from data.files import UI_ELEMENT_DICT, DIR_UI
from data.globalvars import CURRENT_RESOLUTION
from enums.imagealign import ImageAlign
from managers.audiomanager import AudioManager
from managers.spritemanager import SpriteManager
from utils.mathutils import ClosestNumber


def DrawText(
        text: str,
        surface: pygame.Surface,
        font: Font,
        pos: (int, int),
        align: ImageAlign = ImageAlign.TOP_LEFT,
        scale: float = 1,
        color: (int, int, int) = (237, 230, 200)):
    res_scale = RESOLUTIONS[CURRENT_RESOLUTION][1]
    scale *= res_scale
    image = font.render(text, True, color)
    width = image.get_width()
    height = image.get_height()
    image = pygame.transform.scale(image, (int(width * scale), int(height * scale))).convert_alpha()
    rect = image.get_rect()
    if align == ImageAlign.TOP_LEFT:
        rect.topleft = pos
    elif align == ImageAlign.TOP_RIGHT:
        rect.topright = pos
    elif align == ImageAlign.CENTER:
        new_pos = (ClosestNumber(int(pos[0] - rect.width / 2), res_scale),
                   ClosestNumber(int(pos[1] - rect.height / 2), res_scale))
        rect.topleft = new_pos
    surface.blit(image, rect)


def DrawImage(image_path: str,
              surface: pygame.Surface,
              pos: (int, int),
              align: ImageAlign = ImageAlign.TOP_LEFT,
              scale: float = 1):
    res_scale = RESOLUTIONS[CURRENT_RESOLUTION][1]
    scale *= res_scale
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale)).convert_alpha()
    rect = image.get_rect()
    if align == ImageAlign.TOP_LEFT:
        rect.topleft = pos
    elif align == ImageAlign.TOP_RIGHT:
        rect.topright = pos
    elif align == ImageAlign.CENTER:
        new_pos = (ClosestNumber(int(pos[0] - rect.width / 2), res_scale),
                   ClosestNumber(int(pos[1] - rect.height / 2), res_scale))
        rect.topleft = new_pos
    surface.blit(image, rect)


def DrawSprite(sprite: pygame.sprite.Sprite,
               surface: pygame.Surface,
               pos: (int, int),
               align: ImageAlign = ImageAlign.TOP_LEFT,
               scale: float = 1):
    image = sprite.image
    if scale != 1:
        image = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))
    rect = image.get_rect()
    if align == ImageAlign.TOP_LEFT:
        rect.topleft = pos
    elif align == ImageAlign.TOP_RIGHT:
        rect.topright = pos
    elif align == ImageAlign.CENTER:
        rect.center = pos
    surface.blit(image, rect)


class Button:
    def __init__(self,
                 image: str,
                 text: str,
                 font: Font,
                 pos: (int, int),
                 image_scale: float = 1,
                 text_scale: float = 1,
                 align: ImageAlign = ImageAlign.TOP_LEFT,
                 action_sound: str = None,
                 sound: str = AUDIO_CLICK,
                 text_offset: tuple[int, int] = (0, 0),
                 text_color: (int, int, int) = (72, 84, 84)):
        res_scale = RESOLUTIONS[CURRENT_RESOLUTION][1]
        image_scale *= res_scale

        self.sprite_normal = pygame.sprite.Sprite()
        self.sprite_normal.image = pygame.image.load(DIR_UI + UI_ELEMENT_DICT[image][0]).convert_alpha()
        self.sprite_normal.image = pygame.transform.scale(
            self.sprite_normal.image,
            (int(self.sprite_normal.image.get_width() * image_scale),
             int(self.sprite_normal.image.get_height() * image_scale))).convert_alpha()
        self.sprite_normal.rect = self.sprite_normal.image.get_rect()
        self.sprite_hover = pygame.sprite.Sprite()
        self.sprite_hover.image = pygame.image.load(DIR_UI + UI_ELEMENT_DICT[image][1]).convert_alpha()
        self.sprite_hover.image = pygame.transform.scale(
            self.sprite_hover.image,
            (int(self.sprite_hover.image.get_width() * image_scale),
             int(self.sprite_hover.image.get_height() * image_scale))).convert_alpha()
        self.sprite_hover.rect = self.sprite_hover.image.get_rect()
        self.sprite_click = pygame.sprite.Sprite()
        self.sprite_click.image = pygame.image.load(DIR_UI + UI_ELEMENT_DICT[image][2]).convert_alpha()
        self.sprite_click.image = pygame.transform.scale(
            self.sprite_click.image,
            (int(self.sprite_click.image.get_width() * image_scale),
             int(self.sprite_click.image.get_height() * image_scale))).convert_alpha()
        self.sprite_click.rect = self.sprite_click.image.get_rect()

        text_image = font.render(text, True, text_color)
        width = text_image.get_width()
        height = text_image.get_height()
        self.text_image = pygame.transform.scale(
            text_image, (int(width * text_scale), int(height * text_scale))).convert_alpha()
        self.text_rect = self.text_image.get_rect()

        if align == ImageAlign.TOP_LEFT:
            self.sprite_normal.rect.topleft = pos
            self.sprite_hover.rect.topleft = pos
            self.sprite_click.rect.topleft = pos
        elif align == ImageAlign.TOP_RIGHT:
            self.sprite_normal.rect.topright = pos
            self.sprite_hover.rect.topright = pos
            self.sprite_click.rect.topright = pos
        elif align == ImageAlign.CENTER:
            new_pos = (ClosestNumber(int(pos[0] - self.sprite_normal.rect.width / 2), res_scale),
                       ClosestNumber(int(pos[1] - self.sprite_normal.rect.height / 2), res_scale))
            self.sprite_normal.rect.topleft = new_pos
            self.sprite_hover.rect.topleft = new_pos
            self.sprite_click.rect.topleft = new_pos

        self.text_rect.center = (self.sprite_normal.rect.center[0] + text_offset[0],
                                 self.sprite_normal.rect.center[1] + text_offset[1])

        self.clicked = False
        self.sound = sound
        self.action_sound = action_sound

    def Draw(self, surface: pygame.Surface):
        action = False
        mouse_pos = pygame.mouse.get_pos()
        image = self.sprite_normal.image
        rect = self.sprite_normal.rect

        if rect.collidepoint(mouse_pos):
            image = self.sprite_hover.image
            rect = self.sprite_hover.rect
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                AudioManager().Play_Sound(self.sound)
                self.clicked = True
            if self.clicked:
                image = self.sprite_click.image
                rect = self.sprite_click.rect
                if not pygame.mouse.get_pressed()[0]:
                    if self.action_sound:
                        AudioManager().Play_Sound(self.action_sound)
                    action = True

        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        surface.blit(image, rect)
        surface.blit(self.text_image, self.text_rect)

        return action


class ScaledButton:
    def __init__(self,
                 image: str,
                 text: str,
                 font: Font,
                 pos: (int, int),
                 image_scale: float = 1,
                 text_scale: float = 1,
                 align: ImageAlign = ImageAlign.TOP_LEFT,
                 padding: int = 1,
                 action_sound: str = None,
                 sound: str = AUDIO_CLICK,
                 text_color: (int, int, int) = (72, 84, 84)):
        res_scale = RESOLUTIONS[CURRENT_RESOLUTION][1]
        padding *= res_scale
        pos = (ClosestNumber(pos[0], res_scale), ClosestNumber(pos[1], res_scale))

        text_image = font.render(text, False, text_color)
        text_width = int(text_image.get_width() * text_scale)
        text_height = int(text_image.get_height() * text_scale)
        text_image = pygame.transform.scale(
            text_image, (int(text_width), int(text_height)))

        bs = SpriteManager().button_sprites[image]
        height = bs[UI_NORMAL][UI_MIDDLE].get_height()
        width = text_width + bs[UI_NORMAL][UI_LEFT].get_width() + bs[UI_NORMAL][UI_RIGHT].get_width() + padding

        self.normal_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.normal_surface.blit(bs[UI_NORMAL][UI_LEFT], (0, 0))
        self.normal_surface.blit(bs[UI_NORMAL][UI_RIGHT],
                                 (width - bs[UI_NORMAL][UI_RIGHT].get_width(), 0))
        for i in range(bs[UI_NORMAL][UI_LEFT].get_width(),
                       width - bs[UI_NORMAL][UI_RIGHT].get_width()):
            self.normal_surface.blit(bs[UI_NORMAL][UI_MIDDLE], (i, 0))

        self.hover_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.hover_surface.blit(bs[UI_HOVER][UI_LEFT], (0, 0))
        self.hover_surface.blit(bs[UI_HOVER][UI_RIGHT],
                                (width - bs[UI_HOVER][UI_RIGHT].get_width(), 0))
        for i in range(bs[UI_HOVER][UI_LEFT].get_width(),
                       width - bs[UI_HOVER][UI_RIGHT].get_width()):
            self.hover_surface.blit(bs[UI_HOVER][UI_MIDDLE], (i, 0))

        self.click_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.click_surface.blit(bs[UI_CLICK][UI_LEFT], (0, 0))
        self.click_surface.blit(bs[UI_CLICK][UI_RIGHT],
                                (width - bs[UI_CLICK][UI_RIGHT].get_width(), 0))
        for i in range(bs[UI_CLICK][UI_LEFT].get_width(),
                       width - bs[UI_CLICK][UI_RIGHT].get_width()):
            self.click_surface.blit(bs[UI_CLICK][UI_MIDDLE], (i, 0))

        self.normal_rect = self.normal_surface.get_rect()
        self.hover_rect = self.hover_surface.get_rect()
        self.click_rect = self.click_surface.get_rect()

        if image in SpriteManager().button_decals:
            bd = SpriteManager().button_decals[image]

            if bd[UI_NORMAL][1] == ImageAlign.TOP_LEFT:
                n_align = bd[UI_NORMAL][2]
            elif bd[UI_NORMAL][1] == ImageAlign.CENTER:
                n_align = (self.normal_rect.center[0] + bd[UI_NORMAL][2][0], self.normal_rect.center[1] + bd[UI_NORMAL][2][1])
            else:
                n_align = (self.normal_rect.width + bd[UI_NORMAL][2][0] - bd[UI_NORMAL][0].get_width(), 0 + bd[UI_NORMAL][2][1])

            if bd[UI_HOVER][1] == ImageAlign.TOP_LEFT:
                h_align = bd[UI_HOVER][2]
            elif bd[UI_HOVER][1] == ImageAlign.CENTER:
                h_align = (self.hover_rect.center[0] + bd[UI_HOVER][2][0], self.hover_rect.center[1] + bd[UI_HOVER][2][1])
            else:
                h_align = (self.hover_rect.width + bd[UI_HOVER][2][0] - bd[UI_HOVER][0].get_width(), 0 + bd[UI_HOVER][2][1])

            if bd[UI_CLICK][1] == ImageAlign.TOP_LEFT:
                c_align = bd[UI_CLICK][2]
            elif bd[UI_CLICK][1] == ImageAlign.CENTER:
                c_align = (self.click_rect.center[0] + bd[UI_CLICK][2][0], self.click_rect.center[1] + bd[UI_CLICK][2][1])
            else:
                c_align = (self.click_rect.width + bd[UI_CLICK][2][0] - bd[UI_CLICK][0].get_width(), 0 + bd[UI_CLICK][2][1])

            self.normal_surface.blit(bd[UI_NORMAL][0], n_align)
            self.hover_surface.blit(bd[UI_HOVER][0], h_align)
            self.click_surface.blit(bd[UI_CLICK][0], c_align)

        self.normal_surface.blit(text_image, ((width - text_width) / 2, (height - text_height) / 2))
        self.hover_surface.blit(text_image, ((width - text_width) / 2, (height - text_height) / 2))
        self.click_surface.blit(text_image, ((width - text_width) / 2, (height - text_height) / 2))

        scale = image_scale * res_scale
        
        self.normal_surface = pygame.transform.scale(
            self.normal_surface, (self.normal_rect.width * scale, self.normal_rect.height * scale))
        self.hover_surface = pygame.transform.scale(
            self.hover_surface, (self.hover_rect.width * scale, self.hover_rect.height * scale))
        self.click_surface = pygame.transform.scale(
            self.click_surface, (self.click_rect.width * scale, self.click_rect.height * scale))

        self.normal_rect = self.normal_surface.get_rect()
        self.hover_rect = self.hover_surface.get_rect()
        self.click_rect = self.click_surface.get_rect()

        if align == ImageAlign.TOP_LEFT:
            self.normal_rect.topleft = pos
            self.hover_rect.topleft = pos
            self.click_rect.topleft = pos
        elif align == ImageAlign.TOP_RIGHT:
            self.normal_rect.topright = pos
            self.hover_rect.topright = pos
            self.click_rect.topright = pos
        elif align == ImageAlign.CENTER:
            new_pos = (ClosestNumber(int(pos[0] - self.normal_rect.width / 2), res_scale),
                       ClosestNumber(int(pos[1] - self.normal_rect.height / 2), res_scale))
            self.normal_rect.topleft = new_pos
            self.hover_rect.topleft = new_pos
            self.click_rect.topleft = new_pos

        self.clicked = False
        self.sound = sound
        self.action_sound = action_sound

    def Draw(self, surface: pygame.Surface):
        action = False
        mouse_pos = pygame.mouse.get_pos()
        image = self.normal_surface
        rect = self.normal_rect

        if rect.collidepoint(mouse_pos):
            image = self.hover_surface
            rect = self.hover_rect
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                AudioManager().Play_Sound(self.sound)
                self.clicked = True
            if self.clicked:
                image = self.click_surface
                rect = self.click_rect
                if not pygame.mouse.get_pressed()[0]:
                    if self.action_sound:
                        AudioManager().Play_Sound(self.action_sound)
                    action = True

        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        surface.blit(image, rect)

        return action
