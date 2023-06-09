import pygame.draw
from pygame import Surface, Rect
from robingame.objects import Entity

from automata.backends import Backend
from automata.controllers import Controller
from automata.frontends import Frontend


class Viewer(Entity):
    """
    inherits Entity
    contains Backend
    contains Frontend
    contains Controller
    """

    backend: Backend  # handles game logic
    frontend: Frontend  # handles drawing
    controller: Controller  # handles user input

    rect: Rect  # to store own position

    def __init__(
        self, rect: Rect, backend: Backend, frontend: Frontend, controller: Controller = None
    ):
        super().__init__()
        self.rect = Rect(rect)
        self.image = Surface(self.rect.size)
        self.backend = backend
        self.frontend = frontend
        self.controller = controller

    def update(self):
        super().update()
        self.backend.update()
        mouse_pos = pygame.mouse.get_pos()
        is_focused = self.rect.contains((*mouse_pos, 0, 0))
        if self.controller and is_focused:
            self.controller.update(frontend=self.frontend, backend=self.backend)

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        self.frontend.draw(surface=self.image, automaton=self.backend.automaton, debug=debug)
        surface.blit(self.image, self.rect)
        if debug:
            pygame.draw.rect(surface, (255, 0, 0), self.rect, 1)
