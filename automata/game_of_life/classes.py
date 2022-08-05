from pygame.sprite import AbstractGroup

from automata.game_of_life import threshold
from base.objects import Entity

Coord = tuple[int, int]


class InfiniteBoard(Entity):
    contents: dict[Coord:bool]

    def __init__(self, contents=None, *groups: AbstractGroup) -> None:
        super().__init__(*groups)
        self.contents = contents or dict()

    def update(self):
        super().update()
        new = self.contents.copy()
        # game of life rules here
        for coord, alive in self.contents.items():
            live_neighbours = self.live_neighbours(coord)

            # 1. Any live cell with fewer than two live neighbours dies, as if by underpopulation.
            # 2. Any live cell with two or three live neighbours lives on to the next generation.
            # 3. Any live cell with more than three live neighbours dies, as if by overpopulation.
            if alive and threshold.UNDERPOPULATION <= live_neighbours <= threshold.OVERPOPULATION:
                new[coord] = True

            # 4. Any dead cell with exactly three live neighbours becomes a live cell, as if by
            # reproduction.
            if not alive and live_neighbours == threshold.REPRODUCTION:
                new[coord] = True

    def get_neighbours(self, coord: Coord):
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
        neighbours = [self.contents[coord] for coord in directions if coord in self.contents]
        return neighbours

    def live_neighbours(self, coord: Coord):
        return self.get_neighbours(coord).count(True)
