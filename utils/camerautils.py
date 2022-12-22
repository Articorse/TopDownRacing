import pygame
import pymunk
from pygame import Vector2

from data.constants import CAMERA_MOVEMENT_SPEED


def CenterCamera(
        camera: pygame.Vector2,
        race_manager,
        target: pymunk.Vec2d,
        screen_size: Vector2,
        smoothing: bool = True):
    camera_target_pos = pygame.Vector2(-target.x, -target.y) + screen_size / 2
    if smoothing:
        camera = camera_target_pos + (camera - camera_target_pos) * CAMERA_MOVEMENT_SPEED
    else:
        camera = camera_target_pos
    if camera.x < -race_manager.track.size.x + screen_size.x:
        camera.x = -race_manager.track.size.x + screen_size.x
    if camera.x > 0:
        camera.x = 0
    if camera.y < -race_manager.track.size.y + screen_size.y:
        camera.y = -race_manager.track.size.y + screen_size.y
    if camera.y > 0:
        camera.y = 0
    return camera


def GetCameraCenter(camera: pygame.Vector2, screen_size: Vector2):
    return camera + screen_size / 2
