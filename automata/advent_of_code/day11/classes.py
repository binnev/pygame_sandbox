import matplotlib
import numpy
from pygame import Color
from pygame.surface import Surface

from automata.advent_of_code.game import AdventOfCodeGame
from fighting_game.objects import Entity


raw = """7777838353
2217272478
3355318645
2242618113
7182468666
5441641111
4773862364
5717125521
7542127721
4576678341"""


def init():
    return [list(map(int, row)) for row in raw.splitlines()]


class Octopus:
    def __init__(self, energy):
        self.energy = energy

    def __repr__(self):
        return f"{self.energy}"

    def __str__(self):
        return self.__repr__()


class Board(Entity):
    game: AdventOfCodeGame
    scaling = 13
    colormap = matplotlib.cm.twilight
    energy_levels = 13
    size = 75

    def __init__(self, game):
        self.game = game
        # self.contents = [list(map(Octopus, row)) for row in init()]
        self.contents = [
            list(map(Octopus, row))
            for row in numpy.array(
                numpy.random.random((self.size, self.size)) * self.energy_levels, dtype=int
            )
        ]
        self.calculate_colours()
        super().__init__()

    def __repr__(self):
        return "\n".join("".join(map(str, row)) for row in self.contents)

    def update(self):
        flashes = set()
        for oct in self.octopi:
            oct.energy += 1

        ready_to_flash = [
            (x, y, oct)
            for y, row in enumerate(self.contents)
            for x, oct in enumerate(row)
            if oct.energy > (self.energy_levels - 1) and oct not in flashes
        ]
        while ready_to_flash:
            ready_to_flash = [
                (x, y, oct)
                for y, row in enumerate(self.contents)
                for x, oct in enumerate(row)
                if oct.energy > (self.energy_levels - 1) and oct not in flashes
            ]
            for x, y, oct in ready_to_flash:
                flashes.add(oct)
                for neighbour in self.get_neighbours(x, y):
                    neighbour.energy += 1

        for oct in flashes:
            oct.energy = 0
        return flashes

    def get_neighbours(self, x, y):
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
        octos = []
        for x, y in directions:
            if x < 0 or y < 0:
                continue
            try:
                octos.append(self.contents[y][x])
            except IndexError:
                pass
        return octos

    @property
    def octopi(self):
        return [o for row in self.contents for o in row]

    def calculate_colours(self):
        """Sample a colormap based on the longest ruleset of child ants"""
        samples = numpy.linspace(0, 1, self.energy_levels)
        colours = {
            ii: tuple(map(int, color[:3])) for ii, color in enumerate(self.colormap(samples) * 256)
        }
        # colours[0] = Color("white")
        self.colours = colours

    def draw(self, surface: Surface, debug: bool = False):
        # draw base board
        for y, row in enumerate(self.contents):
            for x, cell in enumerate(row):
                pixel = Surface((self.scaling, self.scaling))
                colour = self.colours[cell.energy]
                pixel.fill(colour[:3])
                screen_x, screen_y = x * self.scaling, y * self.scaling
                surface.blit(pixel, (screen_x, screen_y))
        super().draw(surface, debug)
