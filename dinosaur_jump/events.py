from dataclasses import dataclass

import pygame


game_over = pygame.event.custom_type()


@dataclass
class AddBullet:
    type = pygame.event.custom_type()
    x: int
    y: int
    u: int
    v: int
