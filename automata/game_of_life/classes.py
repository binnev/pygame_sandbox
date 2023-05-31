import math

import matplotlib
import numpy
from pygame import Surface, Color
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

    viewport_center: Coord
    scale: int
    num_colors: int
    colormap = matplotlib.cm.viridis_r

    def __init__(
        self,
        *args,
        viewport_center: Coord = (0, 0),
        scale: int = 100,
        num_colors: int = 100,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.scale = scale
        self.num_colors = num_colors
        self.viewport_center = viewport_center
        self.calculate_colors()

    def update(self):
        pass  # temporarily freeze

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)

        # create a smaller image on which the cells can be drawn with one pixel each
        width, height = surface.get_rect().size
        small_img = Surface((math.ceil(width / self.scale), math.ceil(height / self.scale)))
        small_img.fill(Color("dark grey"))
        small_rect = small_img.get_rect()
        small_rect.center = self.viewport_center
        x_offset = self.viewport_center[0] - (small_rect.width // 2)
        y_offset = self.viewport_center[1] - (small_rect.height // 2)

        # filter for cells that will be visible
        to_draw = {
            coord: age
            for coord, age in self.contents.items()
            if small_rect.contains((*coord, 1, 1))  # 1x1 pixel at coord location
        }

        # draw 1 pixel for each cell in the small image
        for (x, y), age in to_draw.items():
            color = self.get_color(age)
            xy = (
                x - x_offset,
                y - y_offset,
            )
            small_img.set_at(xy, color)

        big_img = scale_image(small_img, self.scale)  # scale up
        big_img = big_img.subsurface(surface.get_rect())  # crop to screen size

        surface.blit(big_img, (0, 0))

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
