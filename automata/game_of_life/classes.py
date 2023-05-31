import math

import matplotlib
import numpy
from pygame import Surface, Color, Rect
from robingame.image import scale_image
from robingame.objects import Entity, Group
from robingame.utils import SparseMatrix, Coord

from automata.game_of_life import threshold


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
    Class to draw a Game of Life board onto a surface.
    Scaling is absolute:
        1x scale means each cell is 1x1 px.
        10x scale means each cell is 10x10 px.
    where 'px' means screen pixels
    """

    viewport_center_xy: tuple[float, float]  # coordinate on which to center the viewport
    scale: int
    num_colors: int
    colormap = matplotlib.cm.viridis_r

    def __init__(
        self,
        *args,
        viewport_center_xy: tuple[float, float] = (0.0, 0.0),
        scale: int = 100,
        num_colors: int = 100,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.scale = scale
        self.num_colors = num_colors
        self.viewport_center_xy = viewport_center_xy
        self.calculate_colors()

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

        # 1. Choose viewport in xy coordinates to filter for visible cells
        # 2. Round out to nearest int, record x/y min/max range.
        viewport_center_x, viewport_center_y = self.viewport_center_xy
        screen_width, screen_height = surface.get_rect().size
        viewport_width = math.ceil(screen_width / self.scale)
        viewport_height = math.ceil(screen_height / self.scale)
        viewport = Rect(0, 0, viewport_width, viewport_height)
        viewport = viewport.inflate(2, 2)
        viewport.center = self.viewport_center_xy

        # 3. Record offset from absolute xy coords to small_img coords (ij)
        i0, j0 = viewport.topleft

        # 4. Create small bitmap on which to draw pixels
        small_img = Surface(viewport.size)
        small_img.fill(Color("dark grey"))

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
        # print(f"Population {len(self.contents)}, drew {len(to_draw)}")

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
