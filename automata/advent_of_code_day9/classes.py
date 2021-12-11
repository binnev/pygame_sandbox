import matplotlib
import numpy
from pygame import Color
from pygame.surface import Surface

from automata.advent_of_code_day9.game import AdventOfCodeGame
from fighting_game.objects import Entity


class Caverns(Entity):
    game: AdventOfCodeGame
    scaling = 9
    colormap = matplotlib.cm.viridis

    def __init__(self, game, raw):
        self.raw = raw
        self.input = [list(map(int, row)) for row in raw.splitlines()]
        self.calculate_colours()
        self.low_points = self.find_low_points(self.input)
        self.basin_sizes = []
        self.explored = set()
        self.reset_search()
        super().__init__()

    def reset_search(self):
        low_point = self.low_points.pop()
        self.basin = {low_point}

    def bfs_step(self):
        basin_size = len(self.basin)
        for x, y in self.basin:
            current_height = self.input[y][x]
            neighbours = self.get_neighbours(self.input, x, y)
            higher_neighbours = filter(lambda key: 9 > neighbours[key] > current_height, neighbours)
            self.basin = self.basin.union(higher_neighbours)
        # if self.basin didn't grow, we're done
        if len(self.basin) == basin_size:
            if self.low_points:
                self.reset_search()
            else:
                pass  # completed puzzle

    def update(self):
        self.bfs_step()
        self.explored = self.explored.union(self.basin)
        super().update()

    def draw(self, surface: Surface, debug: bool = False):
        # draw base board
        for y, row in enumerate(self.input):
            for x, cell in enumerate(row):
                pixel = Surface((self.scaling, self.scaling))
                colour = self.colours[cell]
                pixel.fill(colour[:3])
                screen_x, screen_y = x * self.scaling, y * self.scaling
                surface.blit(pixel, (screen_x, screen_y))

        # draw explored
        for x, y in self.explored:
            pixel = Surface((self.scaling, self.scaling))
            colour = Color("orange")
            pixel.fill(colour[:3])
            screen_x, screen_y = x * self.scaling, y * self.scaling
            surface.blit(pixel, (screen_x, screen_y))

        # draw current basin
        for x, y in self.basin:
            pixel = Surface((self.scaling, self.scaling))
            colour = Color("red")
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

    def find_low_points(self, input):
        low_points = []
        for y, row in enumerate(input):
            for x, cell in enumerate(row):
                neighbours = self.get_neighbours(input, x, y).values()
                if cell < min(neighbours):
                    low_points.append((x, y))
        return low_points

    def get_neighbours(self, input, x, y):
        neighbours = {}
        directions = [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)]
        for x, y in directions:
            if x < 0 or y < 0:
                continue
            try:
                neighbours[(x, y)] = input[y][x]
            except IndexError:
                pass
        return neighbours
