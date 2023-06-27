import pygame.draw
from pygame import Surface, Rect, Color
from robingame.objects import Entity
from robingame.text.font import fonts

from automata.backend import Backend
from automata.input_handler import InputHandler
from automata.frontend import Frontend
from automata.timer import Timer
from automata.viewport_handler import ViewportHandler, DefaultViewportHandler


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

    TODO:
        [x] zoom: E / Q
        [x] zoom: mousewheel
        [x] change ticks_per_update: left / right
        [x] change iterations_per_update: up / down
        [x] center on centroid: C
        [x] pan: WASD
        [x] pause: Space
        [x] forward 1 (when paused): >
        [x] back 1 (when paused): <
        [ ] pan: drag w mouse
        [ ] place / remove cell: L / R mouse button
        [x] save / load to file
    """

    backend: Backend  # handles game logic
    frontend: Frontend  # handles drawing
    controller: InputHandler  # handles user input

    rect: Rect  # to store own position

    def __init__(
        self,
        rect: Rect,
        backend: Backend,
        frontend: Frontend,
        viewport_handler: ViewportHandler = None,
        controller: InputHandler = None,
    ):
        super().__init__()
        self.rect = Rect(rect)
        self.image = Surface(self.rect.size)
        self.backend = backend
        self.frontend = frontend
        self.controller = controller
        self.viewport_handler = viewport_handler or DefaultViewportHandler(
            x=0,
            y=0,
            width=self.image.get_width() // 4,
            height=self.image.get_height() // 4,
        )

    def update(self):
        """Note: we are not doing self.backend.update() here, because multiple viewers might
        listen to the same backend, and we don't want to update it multiple times."""
        super().update()
        mouse_pos = pygame.mouse.get_pos()
        is_focused = self.rect.contains((*mouse_pos, 0, 0))
        if self.controller and is_focused:
            self.controller.update(viewport_handler=self.viewport_handler, backend=self.backend)

    def draw(self, surface: Surface, debug: bool = False):
        with Timer() as draw_timer:
            super().draw(surface, debug)
            self.frontend.draw(
                surface=self.image,
                automaton=self.backend.automaton,
                viewport=self.viewport_handler.viewport,
                debug=debug,
            )
            pygame.draw.rect(self.image, Color("white"), self.image.get_rect(), 1)
        surface.blit(self.image, self.rect)
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
            fonts.cellphone_white.render(surface, text, x=self.rect.x, y=self.rect.y, scale=1.5)
