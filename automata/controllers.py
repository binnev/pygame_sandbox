import pygame
from typing import Protocol

from robingame.input import EventQueue

from automata.backends import Backend
from automata.frontends import Frontend


class Controller(Protocol):
    def update(self, frontend: Frontend, backend: Backend):
        ...


class KeyboardController:
    """
    Implements Controller
    """

    def update(self, frontend: Frontend, backend: Backend):
        keys_down = pygame.key.get_pressed()
        if keys_down[pygame.K_e]:
            frontend.zoom(0.2)
        if keys_down[pygame.K_q]:
            frontend.zoom(-0.2)
        if keys_down[pygame.K_w]:
            frontend.pan(y=-1)
        if keys_down[pygame.K_s]:
            frontend.pan(y=1)
        if keys_down[pygame.K_a]:
            frontend.pan(x=-1)
        if keys_down[pygame.K_d]:
            frontend.pan(x=1)

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
