import matplotlib
import numpy
from pygame import Surface, Color
from pygame.sprite import AbstractGroup

from automata.game_of_life import threshold
from base.objects import Entity
from base.text.font import fonts
from base.utils import SparseMatrix, Coord, draw_text


class InfiniteBoard(Entity):
    contents: SparseMatrix[Coord:int]
    scaling = 100
    x_offset = 50
    y_offset = 50
    num_colors = 100
    colormap = matplotlib.cm.viridis_r

    def __init__(
        self,
        contents=None,
        overpopulation_threshold=threshold.OVERPOPULATION,
        underpopulation_threshold=threshold.UNDERPOPULATION,
        reproduction_threshold=threshold.REPRODUCTION,
        *groups: AbstractGroup,
    ) -> None:
        super().__init__(*groups)
        self.contents = SparseMatrix(contents or {})
        self.calculate_colors()
        self.overpopulation_threshold = overpopulation_threshold
        self.underpopulation_threshold = underpopulation_threshold
        self.reproduction_threshold = reproduction_threshold

    def update(self):
        super().update()
        new = SparseMatrix()

        dead_neighbours = set()

        # iterate over live cells
        for coord, age in self.contents.items():

            # 1. Any live cell with fewer than two live neighbours dies, as if by underpopulation.
            # 2. Any live cell with two or three live neighbours lives on to the next generation.
            # 3. Any live cell with more than three live neighbours dies, as if by overpopulation.
            live_neighbours = len(self.live_neighbours(coord))
            if self.underpopulation_threshold <= live_neighbours <= self.overpopulation_threshold:
                new[coord] = age + 1

            # Gather dead neighbours for later analysis. Put them in a set to avoid duplicates.
            # Here because we are using a sparse matrix that doesn't store "dead" values,
            # we iterate over the neighbours of live cells, since these are the only dead cells
            # that can become alive
            dead_neighbours.update(self.dead_neighbours(coord))

        for coord in dead_neighbours:
            # 4. Any dead cell with exactly three live neighbours becomes a live cell, as if by
            # reproduction.
            if len(self.live_neighbours(coord)) == self.reproduction_threshold:
                new[coord] = 1

        self.contents = new

    def neighbours(self, coord: Coord) -> dict[Coord:bool]:
        x, y = coord
        directions = [
            (x - 1, y - 1),
            (x - 1, y),
            (x - 1, y + 1),
            (x, y - 1),
            (x, y + 1),
            (x + 1, y - 1),
            (x + 1, y),
            (x + 1, y + 1),
        ]
        return {coord: self.contents.get(coord, False) for coord in directions}

    def live_neighbours(self, coord: Coord) -> dict[Coord:bool]:
        return {n: alive for n, alive in self.neighbours(coord).items() if alive}

    def dead_neighbours(self, coord: Coord) -> dict[Coord:bool]:
        return {n: alive for n, alive in self.neighbours(coord).items() if not alive}

    def draw(self, surface: Surface, debug: bool = False):
        screen_width, screen_height = screen_size = surface.get_size()
        autoscale = False
        for xy, age in self.contents.items():
            sx, sy = self.contents.screen_coords(xy, self.scaling, self.x_offset, self.y_offset)
            if not autoscale and (sx < 0 or sx > screen_width or sy < 0 or sy > screen_height):
                autoscale = True
            pixel = Surface((self.scaling, self.scaling))
            color = self.get_color(age)
            pixel.fill(color)
            surface.blit(pixel, (sx, sy))
        if autoscale:
            self.scaling, self.x_offset, self.y_offset = self.contents.scale_to_screen(screen_size)

        text = "\n".join(
            [
                f"{self.underpopulation_threshold=}",
                f"{self.overpopulation_threshold=}",
                f"{self.reproduction_threshold=}",
            ]
        )
        fonts.cellphone_white.render(surface, text, x=surface.get_rect().centerx - 50, scale=2)
        super().draw(surface, debug)

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
