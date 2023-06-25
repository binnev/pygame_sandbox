import time

import pygame.draw
from pygame import Surface, Rect, Color
from robingame.objects import Entity
from robingame.text.font import fonts

from automata.backends import Backend
from automata.controllers import Controller
from automata.frontends import Frontend
from automata.timer import Timer


class Viewer(Entity):
    """
    A window to view a SparseMatrix-based automaton.
    The Backend does the iterating (multiple viewers can listen to the same Backend)
    The Frontend does the drawing
    The Controller handles user inputs / interaction with the automaton

    Based on the choice of backend/frontend/controller the user can compose various types of
    viewer -- e.g. a non-interactive minimap or a fully interactive main map.

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
        self,
        rect: Rect,
        backend: Backend,
        frontend: Frontend,
        controller: Controller = None,
    ):
        super().__init__()
        self.rect = Rect(rect)
        self.image = Surface(self.rect.size)
        self.backend = backend
        self.frontend = frontend
        self.controller = controller

    def update(self):
        """Note: we are not doing self.backend.update() here, because multiple viewers might
        listen to the same backend, and we don't want to update it multiple times."""
        super().update()
        mouse_pos = pygame.mouse.get_pos()
        is_focused = self.rect.contains((*mouse_pos, 0, 0))
        if self.controller and is_focused:
            self.controller.update(frontend=self.frontend, backend=self.backend)

    def draw(self, surface: Surface, debug: bool = False):
        with Timer() as draw_timer:
            super().draw(surface, debug)
            self.frontend.draw(surface=self.image, automaton=self.backend.automaton, debug=debug)
            pygame.draw.rect(self.image, Color("white"), self.image.get_rect(), 1)
        if debug:
            text = "\n".join(
                [
                    f"tick: {self.tick}",  # more introspection could be a problem...
                    f"draw time: {draw_timer.time:0.5f}",
                    f"update time: {self.backend._update_time:0.5f}",
                    f"ticks_per_update: {self.backend.ticks_per_update}",
                    f"iterations_per_update: {self.backend.iterations_per_update}",
                    f"world size: {self.backend.automaton.contents.size}",
                    f"world limits: {self.backend.automaton.contents.limits}",
                    f"matrix len: {len(self.backend.automaton.contents)}",
                ]
            )
            fonts.cellphone_white.render(self.image, text, scale=1.5)
            pygame.draw.rect(self.image, Color("red"), self.image.get_rect(), 1)
        surface.blit(self.image, self.rect)
