import pygame
import pymunk
from pygame import Vector2
from pymunk import Vec2d
from data.constants import SF_WALL, COLLTYPE_TRACK, COLLTYPE_CHECKPOINT, TRACK_PADDING, SCREEN_SIZE
from data.files import ASSETS_DIR, SPRITES_DIR
from enums.racedirection import RaceDirection
from models.trackmodel import TrackModel


class Track:
    def __init__(
            self,
            track_model: TrackModel):
        self.name = track_model.name
        thumb_sp = pygame.sprite.Sprite()
        thumb_sp.image = pygame.image.load(ASSETS_DIR + SPRITES_DIR + track_model.thumbnail_filename).convert()
        thumb_sp.rect = thumb_sp.image.get_rect()
        self.thumbnail_path = thumb_sp
        bg_sp = pygame.sprite.Sprite()
        bg_sp.image = pygame.image.load(ASSETS_DIR + SPRITES_DIR + track_model.background_filename).convert()
        bg_sp.rect = bg_sp.image.get_rect()
        bg_sp.image = pygame.transform.scale(bg_sp.image,
                                             (int(bg_sp.rect.width * track_model.scale),
                                              int(bg_sp.rect.height * track_model.scale)))
        bg_sp.rect = bg_sp.image.get_rect()
        bg_sp.rect.topleft = (0, 0)
        self.background = bg_sp
        self.direction = RaceDirection(track_model.direction)
        self.track_segments: list[list[Vec2d]] = []
        for seg in track_model.track_segments:
            s: list[Vec2d] = []
            for t in seg:
                s.append(Vec2d(*t) * track_model.scale)
            self.track_segments.append(s)
        self.guidepath: list[Vec2d] = []
        for t in track_model.guidepath:
            self.guidepath.append(Vec2d(*t) * track_model.scale)
        self.checkpoints: list[tuple[Vec2d, Vec2d]] = []
        for t in track_model.checkpoints:
            self.checkpoints.append((Vec2d(t[0][0], t[0][1]) * track_model.scale,
                                     Vec2d(t[1][0], t[1][1]) * track_model.scale))
        self.start_position = Vec2d(
            self.checkpoints[0][0].x + self.checkpoints[0][1].x,
            self.checkpoints[0][0].y + self.checkpoints[0][1].y) / 2

        max_x = 0
        max_y = 0
        for seg in self.track_segments:
            for vec in seg:
                max_x = max(max_x, vec.x)
                max_y = max(max_y, vec.y)
        max_x = max(max_x, SCREEN_SIZE.x)
        max_y = max(max_y, SCREEN_SIZE.y)
        if track_model.pad:
            max_x += TRACK_PADDING
            max_y += TRACK_PADDING
        self.size = Vector2(max_x, max_y)

    def AddToSpace(self, space: pymunk.Space):
        track_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        track_body.position = (0, 0)
        track_segments = []
        for seg in self.track_segments:
            for i in range(len(seg) - 1):
                segment = pymunk.Segment(track_body, seg[i], seg[i + 1], 5)
                segment.filter = pymunk.ShapeFilter(categories=SF_WALL)
                segment.collision_type = COLLTYPE_TRACK
                track_segments.append(segment)
            end_segment = pymunk.Segment(track_body, seg[-1], seg[0], 5)
            end_segment.filter = pymunk.ShapeFilter(categories=SF_WALL)
            end_segment.collision_type = COLLTYPE_TRACK
            track_segments.append(end_segment)
        for checkpoint in self.checkpoints:
            segment = pymunk.Segment(track_body, checkpoint[0], checkpoint[1], 5)
            segment.sensor = True
            segment.collision_type = COLLTYPE_CHECKPOINT
            track_segments.append(segment)
        space.add(track_body, *track_segments)
