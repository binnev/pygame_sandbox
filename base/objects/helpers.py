import time
from collections import deque

import pygame
from pygame.color import Color
from pygame.surface import Surface

from base.objects.entity import Entity


class FpsTracker(Entity):
    """Displays a little number in the top right of the window if debug=True"""
    buffer_length = 60

    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.queue = deque(maxlen=self.buffer_length)
        self.font = pygame.font.Font(pygame.font.get_default_font(), 12)

    def update(self):
        t = time.perf_counter()
        self.queue.append(t)
        seconds = self.queue[-1] - self.queue[0]
        self.fps = int(self.buffer_length / seconds) if seconds else 0

    def draw(self, surface: Surface, debug: bool = False):
        if debug:
            text = self.font.render(f"FPS: {self.fps}", True, Color("black"))
            text_rect = text.get_rect()
            text_rect.right = surface.get_rect().right - 10
            text_rect.top = surface.get_rect().top + 10
            background = Surface(text_rect.size)
            background.fill(Color("white"))
            surface.blit(background, text_rect)
            surface.blit(text, text_rect)
