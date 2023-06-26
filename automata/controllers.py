from typing import Protocol

import pygame
from robingame.input import EventQueue

from automata.backends import Backend
from automata.viewport_handler import ViewportHandler


class Controller(Protocol):
    def update(self, viewport_handler: ViewportHandler, backend: Backend):
        """Handle inputs"""


class KeyboardController:
    """
    Implements Controller
    """

    def update(self, viewport_handler: ViewportHandler, backend: Backend):
        keys_down = pygame.key.get_pressed()
        if keys_down[pygame.K_e]:
            viewport_handler.zoom(0.2)
        if keys_down[pygame.K_q]:
            viewport_handler.zoom(-0.2)
        if keys_down[pygame.K_w]:
            viewport_handler.pan(y=-1)
        if keys_down[pygame.K_s]:
            viewport_handler.pan(y=1)
        if keys_down[pygame.K_a]:
            viewport_handler.pan(x=-1)
        if keys_down[pygame.K_d]:
            viewport_handler.pan(x=1)

        for event in EventQueue.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    backend.paused = not backend.paused
                if backend.paused:
                    if event.key == pygame.K_PERIOD:
                        backend.iterate()
                    if event.key == pygame.K_COMMA:
                        backend.back_one()
                if event.key == pygame.K_DOWN:
                    backend.ticks_per_update *= 2
                if event.key == pygame.K_UP:
                    backend.ticks_per_update = max(1, backend.ticks_per_update // 2)
                if event.key == pygame.K_RIGHT:
                    backend.iterations_per_update *= 2
                if event.key == pygame.K_LEFT:
                    backend.iterations_per_update = max(1, backend.iterations_per_update // 2)
