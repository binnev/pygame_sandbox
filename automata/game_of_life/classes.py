import logging
import math

import matplotlib
import numpy
import pygame.mouse
from pygame import Surface, Color, Rect
from robingame.image import scale_image
from robingame.input import EventQueue
from robingame.objects import Entity, Group
from robingame.utils import SparseMatrix, Coord

from automata.game_of_life import threshold

logger = logging.getLogger(__file__)


class InfiniteBoard(Entity):
    """
    This class is solely responsible for calculating the next state in a Game of Life simulation.
    It uses a SparseMatrix to represent only the live cells in order to save memory + computation.
    It is not aware of any meta game stuff like FPS.
    """

    contents: SparseMatrix[Coord:int]

    def __init__(
        self,
        contents=None,
        overpopulation_threshold=threshold.OVERPOPULATION,
        underpopulation_threshold=threshold.UNDERPOPULATION,
        reproduction_threshold=threshold.REPRODUCTION,
        groups: tuple[Group] = (),
    ) -> None:
        super().__init__(*groups)
        self.contents = SparseMatrix(contents or {})
        self.overpopulation_threshold = overpopulation_threshold
        self.underpopulation_threshold = underpopulation_threshold
        self.reproduction_threshold = reproduction_threshold

    def update(self):
        super().update()

        # Sparse matrix to store the coordinates of any cell (live or dead) that has live
        # neighbours, in the form: {coord: number_of_live_neighbours}.
        live_neighbours_matrix = SparseMatrix[Coord:int]()

        # Iterate once over all the currently live cells, and grab the coordinates of their
        # neighbours. For each of these neighbours, add +1 to their live neighbour count.
        # O(n_cells)
        for cell in self.contents:
            for neighbour in self.neighbours(cell):
                count = live_neighbours_matrix.get(neighbour, 0)
                live_neighbours_matrix[neighbour] = count + 1

        # sparse matrix to contain the live cells for the next iteration
        new = SparseMatrix()

        # Iterate once over the live_neighbours_matrix, and use each cell's number of live
        # neighbours to decide if it is alive in the next iteration.
        for cell, live_neighbours in live_neighbours_matrix.items():
            alive = cell in self.contents
            if alive:
                # 2. Any live cell with two or three live neighbours lives on to the next generation.
                if (
                    self.underpopulation_threshold
                    <= live_neighbours
                    <= self.overpopulation_threshold
                ):
                    age = self.contents[cell]
                    new[cell] = age + 1
            else:
                # 4. Any dead cell with exactly three live neighbours becomes a live cell, as if by
                # reproduction.
                if live_neighbours == self.reproduction_threshold:
                    new[cell] = 1

        self.contents = new

    def neighbours(self, coord: Coord) -> tuple[Coord, ...]:
        """
        Get the coordinates of all neighbouring cells, including diagonals.
        """
        x, y = coord
        return (
            (x - 1, y - 1),
            (x - 1, y),
            (x - 1, y + 1),
            (x, y - 1),
            (x, y + 1),
            (x + 1, y - 1),
            (x + 1, y),
            (x + 1, y + 1),
        )


class InfiniteBoardViewer(InfiniteBoard):
    """
    Subclass to draw an InfiniteBoard board onto a surface.
    Scaling is absolute:
        1x scale means each cell is 1x1 px.
        10x scale means each cell is 10x10 px.
    where 'px' means screen pixels
    """

    viewport_center_xy: tuple[float, float]  # coordinate on which to center the viewport
    scale: float
    num_colors: int
    colormap = matplotlib.cm.viridis_r
    background_color = (30,) * 3
    rect: Rect  # position and size of self in screen coordinates
    paused: bool = False

    def __init__(
        self,
        *args,
        viewport_center_xy: tuple[float, float] = (0.0, 0.0),
        scale: float = 10,
        num_colors: int = 100,
        rect: Rect | tuple,
        paused: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.scale = scale
        self.num_colors = num_colors
        self.viewport_center_xy = viewport_center_xy
        self.calculate_colors()
        self.rect = Rect(*rect)
        self.image = Surface(self.rect.size)
        self.paused = paused

    def zoom(self, amount: float):
        self.scale = max(0.1, self.scale + amount)

    def pan(self, x: float = 0, y: float = 0):
        self.viewport_center_xy = (
            self.viewport_center_xy[0] + x,
            self.viewport_center_xy[1] + y,
        )

    def update(self):
        PAN_SPEED = 10 / self.scale
        if not self.paused:
            super().update()
        mouse_pos = pygame.mouse.get_pos()
        is_focused = self.rect.contains((*mouse_pos, 0, 0))

        if is_focused:
            keys_down = pygame.key.get_pressed()
            if keys_down[pygame.K_e]:
                self.zoom(0.2)
            if keys_down[pygame.K_q]:
                self.zoom(-0.2)
            if keys_down[pygame.K_w]:
                self.pan(y=-PAN_SPEED)
            if keys_down[pygame.K_s]:
                self.pan(y=PAN_SPEED)
            if keys_down[pygame.K_a]:
                self.pan(x=-PAN_SPEED)
            if keys_down[pygame.K_d]:
                self.pan(x=PAN_SPEED)

            for event in EventQueue.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    if event.key == pygame.K_PERIOD and self.paused:
                        super().update()
                    if event.key == pygame.K_COMMA and self.paused:
                        raise NotImplementedError("No history implemented yet")
                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        self.zoom(2)
                    else:
                        self.zoom(-2)

    def draw(self, surface: Surface, debug: bool = False):
        """
        xy = sparse matrix coordinates
        ij = small bitmap pixel indices
        ab = large bitmap pixel indices
        uv = screen coordinates
        viewport = Rect in xy-space to select visible cells. Roughly equal to screen_size/scale
        small_img = Surface with same dimensions as viewport (pixels are used to display cells)
        large_img = small_img scaled up to full size
        """
        super().draw(surface, debug)

        # 0. clear old image
        self.image.fill(self.background_color)

        # 1. Choose viewport in xy coordinates to filter for visible cells
        # 2. Round out to nearest int, record x/y min/max range.
        viewport_center_x, viewport_center_y = self.viewport_center_xy
        image_width, image_height = self.image.get_rect().size
        viewport_width = math.ceil(image_width / self.scale)
        viewport_height = math.ceil(image_height / self.scale)
        viewport = Rect(0, 0, viewport_width, viewport_height)
        viewport = viewport.inflate(2, 2)
        viewport.center = self.viewport_center_xy

        # 3. Record offset from absolute xy coords to small_img coords (ij)
        i0, j0 = viewport.topleft

        # 4. Create small bitmap on which to draw pixels
        small_img = Surface(viewport.size)
        small_img.fill(self.background_color)

        # 5. Filter visible cells
        to_draw = {
            coord: age
            for coord, age in self.contents.items()
            if viewport.contains((*coord, 1, 1))  # 1x1 pixel at coord location
        }

        # 6. Draw visible cells on small bitmap
        for (x, y), age in to_draw.items():
            color = self.get_color(age)
            ij = (x - i0, y - j0)  # matrix coords to pixel indices
            small_img.set_at(ij, color)
        logger.info(f"Population {len(self.contents)}, drew {len(to_draw)}")

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
        center_u, center_v = self.image.get_rect().center
        delta_u = center_u - viewport_center_a
        delta_v = center_v - viewport_center_b
        self.image.blit(big_img, (delta_u, delta_v))

        surface.blit(self.image, self.rect)

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
