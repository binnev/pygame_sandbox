import math
from typing import Protocol

import matplotlib
import numpy
import pygame.draw
from pygame import Surface, Color, Rect
from robingame.image import scale_image
from robingame.text.font import fonts

from automata.automatons import Automaton


class Frontend(Protocol):
    def draw(self, surface: Surface, automaton: Automaton, debug: bool = False):
        """Do something with automaton.contents here"""

    def zoom(self, amount: float):
        """
        If amount > 0: zoom in.
        If amount < 0: zoom out.
        """

    def pan(self, x: float = 0, y: float = 0):
        """
        If x > 0: move viewport right. If x < 0: move viewport left.
        If y > 0: move viewport down. If y < 0: move viewport up.
        """


class DeadSimpleFrontend:
    """Uses the bitmap method and just aligns the top left corners"""

    scale = 5
    background_color = Color("dark grey")
    x_offset: int = 0
    y_offset: int = 0
    num_colors: int = 100
    colormap = matplotlib.cm.viridis_r

    def __init__(self, num_colors=None):
        self.num_colors = num_colors or self.num_colors
        self.calculate_colors()

    def draw(self, surface: Surface, automaton: Automaton, debug: bool = False):
        surface.fill(self.background_color)
        img = Surface(automaton.contents.size)
        img.fill(self.background_color)
        (x_min, _), (y_min, _) = automaton.contents.limits
        for (x, y), value in automaton.contents.items():
            color = self.get_color(value)
            x += self.x_offset - x_min
            y += self.y_offset - y_min
            img.set_at((x, y), color)
        img = scale_image(img, self.scale)
        if debug:
            pygame.draw.rect(img, Color("red"), img.get_rect(), 1)
        surface.blit(img, (0, 0))

    def zoom(self, amount):
        self.scale = max(0.1, self.scale + amount)

    def pan(self, x: float = 0, y: float = 0):
        PAN_SPEED = 5
        self.x_offset -= x * PAN_SPEED
        self.y_offset -= y * PAN_SPEED

    def calculate_colors(self):
        """Sample a colormap based on the longest ruleset of child ants"""
        samples = numpy.linspace(0, 1, self.num_colors)
        colors = [tuple(map(int, color[:3])) for color in self.colormap(samples) * 256]
        self.colors = colors

    def get_color(self, age: int):
        try:
            return self.colors[age]
        except IndexError:
            return self.colors[-1]


class Minimap:
    """
    Fixed scale
    Always centered
    """

    scale = 1
    viewport_center_xy = (0, 0)  # not used!
    background_color = Color("black")

    def draw(self, surface: Surface, automaton: Automaton, debug: bool = False):
        surface.fill(self.background_color)
        img = Surface(automaton.contents.size)
        img.fill(self.background_color)
        (x_min, _), (y_min, _) = automaton.contents.limits
        for (x, y), age in automaton.contents.items():
            color = Color("white")
            x -= x_min
            y -= y_min
            img.set_at((x, y), color)
        img = scale_image(img, self.scale)
        if debug:
            pygame.draw.rect(img, Color("red"), img.get_rect(), 1)

        rect = img.get_rect()
        rect.center = surface.get_rect().center
        surface.blit(img, rect)

    def zoom(self, amount):
        pass

    def pan(self, x, y):
        pass


class GameOfLifeFrontend:
    """Draws using the bitmap method. 1 cell = 1 pixel, then scale up the bitmap."""

    scale = 4
    viewport_center_xy = (0.0, 0.0)
    background_color = Color("black")

    def viewport_rect(self, image: Surface) -> Rect:
        image_width, image_height = image.get_rect().size
        viewport_width = math.ceil(image_width / self.scale)
        viewport_height = math.ceil(image_height / self.scale)
        viewport = Rect(0, 0, viewport_width, viewport_height)
        viewport = viewport.inflate(2, 2)  # make 1 px bigger on all sides for safety
        viewport.center = self.viewport_center_xy
        return viewport

    def draw(self, surface: Surface, automaton: Automaton, debug: bool = False):
        """
        xy = sparse matrix coordinates
        ij = small bitmap pixel indices
        ab = large bitmap pixel indices
        uv = screen coordinates
        viewport = Rect in xy-space to select visible cells. Roughly equal to screen_size/scale
        small_img = Surface with same dimensions as viewport (pixels are used to display cells)
        large_img = small_img scaled up to full size
        """

        # 1. Choose viewport in xy coordinates to filter for visible cells
        # 2. Round out to nearest int, record x/y min/max range.
        viewport_center_x, viewport_center_y = self.viewport_center_xy
        viewport = self.viewport_rect(surface)

        # 3. Record offset from absolute xy coords to small_img coords (ij)
        i0, j0 = viewport.topleft

        # 4. Create small bitmap on which to draw pixels
        small_img = Surface(viewport.size)
        small_img.fill(self.background_color)

        # 5. Filter visible cells
        to_draw = {
            coord: age
            for coord, age in automaton.contents.items()
            if viewport.contains((*coord, 1, 1))  # 1x1 pixel at coord location
        }

        # 6. Draw visible cells on small bitmap
        for (x, y), age in to_draw.items():
            color = self.get_color(age)
            ij = (x - i0, y - j0)  # matrix coords to pixel indices
            small_img.set_at(ij, color)

        # 7. Scale small bitmap up to full size
        big_img = scale_image(small_img, self.scale)

        # 8. Calculate viewport center position in large bitmap coords
        # small_img pixel index to large_img coords
        # a = scale * i + (scale - 1) / 2
        # b = scale * j + (scale - 1) / 2
        viewport_center_i: float = viewport_center_x - i0
        viewport_center_j: float = viewport_center_y - j0
        viewport_center_a: float = (self.scale * viewport_center_i) + (self.scale - 1) / 2
        viewport_center_b: float = (self.scale * viewport_center_j) + (self.scale - 1) / 2

        # 9. Calculate the uv offset required to position viewport_center_ab on the screen center
        center_u, center_v = surface.get_rect().center
        delta_u = center_u - viewport_center_a
        delta_v = center_v - viewport_center_b
        surface.blit(big_img, (delta_u, delta_v))

        if debug:
            text = "\n".join(
                [
                    # f"tick: {self.tick}",  # more introspection could be a problem...
                    f"scale: {self.scale:0.2f}",
                    # f"ticks_per_update: {self.ticks_per_update}",
                    # f"iterations_per_update: {self.iterations_per_update}",
                ]
            )
            fonts.cellphone_white.render(surface, text, scale=1.5)


class LangtonsAntFrontend:
    def draw(self, surface: Surface, automaton: Automaton, debug: bool = False):
        ...


def accepts_frontend(a: Frontend):
    print(a)
