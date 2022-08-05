from pygame import Surface, Color
from pygame.sprite import AbstractGroup

from automata.game_of_life import threshold
from base.objects import Entity
from base.utils import SparseMatrix, Coord


class InfiniteBoard(Entity):
    contents: SparseMatrix
    scaling = 10
    x_offset = 50
    y_offset = 50

    def __init__(self, contents=None, *groups: AbstractGroup) -> None:
        super().__init__(*groups)
        self.contents = SparseMatrix(contents or {})

    def update(self):
        super().update()
        new = SparseMatrix()

        # iterate over live cells
        for coord in self.contents:

            # 1. Any live cell with fewer than two live neighbours dies, as if by underpopulation.
            # 2. Any live cell with two or three live neighbours lives on to the next generation.
            # 3. Any live cell with more than three live neighbours dies, as if by overpopulation.
            live_neighbours = len(self.live_neighbours(coord))
            if threshold.UNDERPOPULATION <= live_neighbours <= threshold.OVERPOPULATION:
                new[coord] = True

            # 4. Any dead cell with exactly three live neighbours becomes a live cell, as if by
            # reproduction.
            # Here because we are using a sparse matrix that doesn't store "dead" values,
            # we iterate over the neighbours of live cells, since these are the only dead cells
            # that can become alive
            for neighbour in self.dead_neighbours(coord):
                if len(self.live_neighbours(neighbour)) == threshold.REPRODUCTION:
                    new[neighbour] = True
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
        for xy, colour_index in self.contents.items():
            sx, sy = self.contents.screen_coords(xy, self.scaling, self.x_offset, self.y_offset)
            if not autoscale and (sx < 0 or sx > screen_width or sy < 0 or sy > screen_height):
                autoscale = True
            pixel = Surface((self.scaling, self.scaling))
            pixel.fill(Color("black"))
            surface.blit(pixel, (sx, sy))
        if autoscale:
            self.scaling, self.x_offset, self.y_offset = self.contents.scale_to_screen(screen_size)
        super().draw(surface, debug)