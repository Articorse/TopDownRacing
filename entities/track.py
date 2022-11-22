import pygame
import pymunk
from enum import Enum
from typing import List
from pygame import Vector2
from pymunk import Vec2d
from data.constants import SF_WALL, COLLTYPE_TRACK, COLLTYPE_CHECKPOINT, TRACK_PADDING, SCREEN_SIZE
from data.files import ASSETS_DIR, SPRITES_DIR


class RaceDirection(str, Enum):
    Up = 'Up'
    Right = 'Right'
    Down = 'Down'
    Left = 'Left'


def _ParseTrackCoordinates(coordinate_set: str):
    coordinate_split = coordinate_set.split(",")
    return Vec2d(int(coordinate_split[0]), int(coordinate_split[1]))


class Track(object):
    def __init__(
            self,
            name: str,
            thumbnail_filename: pygame.sprite.Sprite,
            background_filename: pygame.sprite.Sprite,
            start_position: dict[Vector2],
            direction: str,
            left_wall: list[str],
            right_wall: list[str],
            pad: bool,
            guidepath: list[str],
            checkpoints: list[list[str]]):
        self.name = name
        thumb_sp = pygame.sprite.Sprite()
        thumb_sp.image = pygame.image.load(ASSETS_DIR + SPRITES_DIR + thumbnail_filename).convert()
        thumb_sp.rect = thumb_sp.image.get_rect()
        self.thumbnail_path = thumb_sp
        bg_sp = pygame.sprite.Sprite()
        bg_sp.image = pygame.image.load(ASSETS_DIR + SPRITES_DIR + background_filename).convert()
        bg_sp.rect = bg_sp.image.get_rect()
        self.background_filename = bg_sp
        self.start_position = Vector2(**start_position)
        self.direction = RaceDirection(direction)
        self.left_wall: List[Vec2d] = []
        self.right_wall: List[Vec2d] = []
        self.guidepath: List[Vec2d] = []
        self.checkpoints: List[tuple[Vec2d, Vec2d]] = []

        for vec_string in left_wall:
            self.left_wall.append(_ParseTrackCoordinates(vec_string))
        for vec_string in right_wall:
            self.right_wall.append(_ParseTrackCoordinates(vec_string))
        for vec_string_tuple in checkpoints:
            self.checkpoints.append((_ParseTrackCoordinates(vec_string_tuple[0]),
                                     _ParseTrackCoordinates(vec_string_tuple[1])))
        for vec_string in guidepath:
            self.guidepath.append(_ParseTrackCoordinates(vec_string))

        max_x = 0
        max_y = 0
        for vec in self.left_wall:
            max_x = max(max_x, vec.x)
            max_y = max(max_y, vec.y)
        for vec in self.right_wall:
            max_x = max(max_x, vec.x)
            max_y = max(max_y, vec.y)
        max_x = max(max_x, SCREEN_SIZE.x)
        max_y = max(max_y, SCREEN_SIZE.y)
        if pad:
            max_x += TRACK_PADDING
            max_y += TRACK_PADDING
        self.size = Vector2(max_x, max_y)

    def AddToSpace(self, space: pymunk.Space):
        track_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        track_body.position = (0, 0)
        track_segments = []
        for i in range(len(self.left_wall) - 1):
            segment = pymunk.Segment(track_body, self.left_wall[i], self.left_wall[i + 1], 5)
            segment.filter = pymunk.ShapeFilter(categories=SF_WALL)
            segment.collision_type = COLLTYPE_TRACK
            track_segments.append(segment)
        left_end_segment = pymunk.Segment(track_body, self.left_wall[-1], self.left_wall[0], 5)
        left_end_segment.filter = pymunk.ShapeFilter(categories=SF_WALL)
        left_end_segment.collision_type = COLLTYPE_TRACK
        track_segments.append(left_end_segment)
        for i in range(len(self.right_wall) - 1):
            segment = pymunk.Segment(track_body, self.right_wall[i], self.right_wall[i + 1], 5)
            segment.filter = pymunk.ShapeFilter(categories=SF_WALL)
            segment.collision_type = COLLTYPE_TRACK
            track_segments.append(segment)
        right_end_segment = pymunk.Segment(track_body, self.right_wall[-1], self.right_wall[0], 5)
        right_end_segment.filter = pymunk.ShapeFilter(categories=SF_WALL)
        right_end_segment.collision_type = COLLTYPE_TRACK
        track_segments.append(right_end_segment)
        for checkpoint_tuple in self.checkpoints:
            segment = pymunk.Segment(track_body, checkpoint_tuple[0], checkpoint_tuple[1], 5)
            segment.sensor = True
            segment.collision_type = COLLTYPE_CHECKPOINT
            track_segments.append(segment)
        space.add(track_body, *track_segments)
