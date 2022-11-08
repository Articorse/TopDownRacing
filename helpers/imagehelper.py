import pygame


def RotateImage(image: pygame.Surface, center: (int, int), angle: float):
    new_image = pygame.transform.rotate(image, angle)
    rect = new_image.get_rect(center=center)
    return new_image, rect
