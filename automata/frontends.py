import math
from typing import Protocol

import matplotlib
import numpy
import pygame.draw
from pygame import Surface, Color, Rect
from robingame.image import scale_image
from robingame.utils import Coord

from automata.automatons import Automaton
from automata.viewport_handler import FloatRect


class Frontend(Protocol):
    def draw(
        self, surface: Surface, automaton: Automaton, viewport: FloatRect, debug: bool = False
    ):
        """
        Do something with automaton.contents here.
        viewport is the subset of the matrix we want to draw.
        """


class BitmapFrontend:
    """
    Draws using the bitmap method.
    1 cell = 1 pixel, then scale up the bitmap.
    """

    background_color = Color("black")
    num_colors: int = 100
    colormap = matplotlib.cm.viridis_r

    def __init__(self, num_colors: int = None):
        self.num_colors = num_colors or self.num_colors
        self.calculate_colors()

    def draw(
        self,
        surface: Surface,
        automaton: Automaton,
        viewport: FloatRect,
        debug: bool = False,
    ):
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
        viewport_center_x = viewport[0] + viewport[2] / 2
        viewport_center_y = viewport[1] + viewport[3] / 2
        image_width, image_height = surface.get_size()
        x_scale = image_width / viewport[2]
        y_scale = image_height / viewport[3]
        scale = min(x_scale, y_scale)
        # pad 1 pixel to include any offscreen "halves" of cells, and 1 pixel to account for the
        # fact that Rect rounds the viewport to ints, possibly further in the wrong direction.
        viewport = Rect(*viewport).inflate(4, 4)

        # 3. Record offset from absolute xy coords to small_img coords (ij)
        i0, j0 = viewport.topleft

        # 4. Create small bitmap on which to draw pixels
        small_img = Surface(viewport.size)
        small_img.fill(self.background_color)

        # 5. Filter visible cells
        to_draw = {
            coord: value
            for coord, value in automaton.contents.items()
            if viewport.collidepoint(*coord)
        }

        # 6. Draw visible cells on small bitmap
        for (x, y), value in to_draw.items():
            color = self.get_color(value)
            ij = (x - i0, y - j0)  # matrix coords to pixel indices
            small_img.set_at(ij, color)

        # 7. Scale small bitmap up to full size
        big_img = scale_image(small_img, scale)

        # 8. Calculate viewport center position in large bitmap coords
        # small_img pixel index to large_img coords
        # a = scale * i + (scale - 1) / 2
        # b = scale * j + (scale - 1) / 2
        viewport_center_i: float = viewport_center_x - i0
        viewport_center_j: float = viewport_center_y - j0
        viewport_center_a: float = (scale * viewport_center_i) + (scale - 1) / 2
        viewport_center_b: float = (scale * viewport_center_j) + (scale - 1) / 2

        # 9. Calculate the uv offset required to position viewport_center_ab on the screen center
        center_u, center_v = surface.get_rect().center
        delta_u = center_u - viewport_center_a
        delta_v = center_v - viewport_center_b
        surface.blit(big_img, (delta_u, delta_v))

    def calculate_colors(self):
        """Sample a colormap based on the longest ruleset of child ants"""
        samples = numpy.linspace(0, 1, self.num_colors)
        colors = [tuple(map(int, color[:3])) for color in self.colormap(samples) * 256]
        self.colors = colors

    def get_color(self, value: int):
        try:
            return self.colors[value]
        except IndexError:
            return self.colors[-1]


class DrawRectFrontend(BitmapFrontend):
    """
    Draws each cell using pygame.draw.rect directly onto the Surface passed to the draw method.
    """

    def draw(
        self,
        surface: Surface,
        automaton: Automaton,
        viewport: FloatRect,
        debug: bool = False,
    ):
        """
        xy = sparse matrix coordinates
        uv = screen coordinates
        viewport = Rect in xy-space to select visible cells. Roughly equal to screen_size/scale
        small_img = Surface with same dimensions as viewport (pixels are used to display cells)
        large_img = small_img scaled up to full size
        """

        surface.fill(self.background_color)

        world_width, world_height = automaton.contents.size
        (xmin, xmax), (ymin, ymax) = automaton.contents.limits
        world_rect_xy = Rect(xmin, ymin, world_width, world_height)

        # 1. filter for visible cells using viewport
        # pad 1 pixel to include any offscreen "halves" of cells, and 1 pixel to account for the
        # fact that Rect rounds the viewport to ints, possibly further in the wrong direction.
        viewport_rect_xy = Rect(*viewport)
        visible = {
            coord: value
            for coord, value in automaton.contents.items()
            if viewport_rect_xy.inflate(4, 4).collidepoint(*coord)
        }

        # calculate scale
        image_rect_uv = surface.get_rect()
        transform = Transform(viewport_rect_xy, image_rect_uv)
        viewport_rect_uv = transform.rect(viewport_rect_xy)
        world_rect_uv = transform.rect(world_rect_xy)

        # 6. Draw visible cells in screen coords
        for (x, y), value in visible.items():
            color = self.get_color(value)
            u, v = transform.point((x, y))
            draw_square(surface, color, u, v, transform.scale)

        pygame.draw.rect(surface, Color("red"), viewport_rect_uv, 3)
        pygame.draw.rect(surface, Color("yellow"), world_rect_uv, 3)


def draw_square(surface: Surface, color: Color, u: int, v: int, scale: float):
    pygame.draw.rect(
        surface,
        color,
        Rect(
            u - scale / 2,
            v - scale / 2,
            math.ceil(scale),
            math.ceil(scale),
        ),
    )


def get_scale_offset(viewport_rect_xy: Rect, image_rect_uv: Rect) -> tuple[float, int, int]:
    viewport_rect_uv = viewport_rect_xy.fit(image_rect_uv)
    scale = viewport_rect_uv.width / viewport_rect_xy.width
    u_offset = viewport_rect_uv.x - viewport_rect_xy.x
    v_offset = viewport_rect_uv.y - viewport_rect_xy.y
    return scale, u_offset, v_offset, viewport_rect_uv


def xy_to_uv(x: int, y: int, u_offset: int, v_offset: int, scale: float) -> tuple[float, float]:
    u = x * scale + u_offset
    v = y * scale + v_offset
    return (u, v)


class DrawRectMinimap(DrawRectFrontend):
    def draw(
        self,
        surface: Surface,
        automaton: Automaton,
        viewport: FloatRect,
        debug: bool = False,
    ):
        """
        1. Draw all cells irrespective of scale
        2. Draw viewport
        """
        surface.fill(self.background_color)

        # 1. Choose viewport in xy coordinates to filter for visible cells
        # fit viewport as tightly as possible to world limits
        viewport_rect_xy = Rect(*viewport)
        world_width, world_height = automaton.contents.size
        (xmin, xmax), (ymin, ymax) = automaton.contents.limits
        world_rect_xy = Rect(xmin, ymin, world_width, world_height)
        image_rect_uv = surface.get_rect()
        transform = Transform(world_rect_xy, image_rect_uv)
        viewport_rect_uv = transform.rect(viewport_rect_xy)
        world_rect_uv = transform.rect(world_rect_xy)

        # 6. Draw all cells in screen coords
        for (x, y), value in automaton.contents.items():
            color = self.get_color(value)
            u, v = transform.point((x, y))
            draw_square(surface, color, u, v, transform.scale)

        pygame.draw.rect(surface, Color("red"), viewport_rect_uv, 1)
        pygame.draw.rect(surface, Color("yellow"), world_rect_uv, 1)


class BitmapMinimap:
    """
    Uses bitmap method
    Fixed scale
    Always centered
    """

    scale = 1
    viewport_center_xy = (0, 0)  # not used!
    background_color = Color("black")

    def draw(
        self, surface: Surface, automaton: Automaton, viewport: FloatRect, debug: bool = False
    ):
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


class Transform:
    """
    Convert from xy (matrix coords) -> uv (screen coords) and back
    """

    scale: float
    u_offset: int
    v_offset: int

    def __init__(self, viewport_rect_xy: Rect, image_rect_uv: Rect):
        viewport_rect_uv = viewport_rect_xy.fit(image_rect_uv)
        self.scale = viewport_rect_uv.width / viewport_rect_xy.width
        self.u_offset = viewport_rect_uv.x - viewport_rect_xy.x * self.scale
        self.v_offset = viewport_rect_uv.y - viewport_rect_xy.y * self.scale

    def length(self, length_xy: float) -> float:
        return length_xy * self.scale

    def point(self, point_xy: tuple[float, float]) -> tuple[float, float]:
        x, y = point_xy
        u = x * self.scale + self.u_offset
        v = y * self.scale + self.v_offset
        return (u, v)

    def rect(self, rect_xy: Rect) -> Rect:
        x, y, width_x, height_y = rect_xy
        u, v = self.point((x, y))
        width_u = self.length(width_x)
        height_v = self.length(height_y)
        return Rect(u, v, width_u, height_v)
