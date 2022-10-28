from dataclasses import dataclass

import pygame


@dataclass
class SetValue:
    type = pygame.event.custom_type()
    p1: int
    p2: int