import matplotlib
import numpy
from pygame import Color
from pygame.surface import Surface

from automata.advent_of_code_day9.game import AdventOfCodeDay9Game
from fighting_game.objects import Entity


class Caverns(Entity):
    game: AdventOfCodeDay9Game
    scaling = 9
    colormap = matplotlib.cm.viridis

    def __init__(self, game, raw):
        self.raw = raw
        self.input = [list(map(int, row)) for row in raw.splitlines()]
        self.calculate_colours()
        super().__init__()

    def update(self):
        super().update()

    def draw(self, surface: Surface, debug: bool = False):
        for y, row in enumerate(self.input):
            for x, cell in enumerate(row):
                pixel = Surface((self.scaling, self.scaling))
                colour = self.colours[cell]
                pixel.fill(colour[:3])
                screen_x, screen_y = x * self.scaling, y * self.scaling
                surface.blit(pixel, (screen_x, screen_y))

        super().draw(surface, debug)

    def calculate_colours(self):
        """Sample a colormap based on the longest ruleset of child ants"""
        samples = numpy.linspace(0, 1, 9)
        colours = {
            ii: tuple(map(int, color[:3])) for ii, color in enumerate(self.colormap(samples) * 256)
        }
        colours[9] = Color("black")
        self.colours = colours
