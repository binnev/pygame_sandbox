from typing import Tuple

import matplotlib
import numpy
from pygame.surface import Surface

from automata.langtons_ant.game import LangtonsAntGame
from robingame.objects import Entity, Group
from robingame.utils import SparseMatrix


class Board(Entity):
    """The board on which the ants crawl"""

    game: LangtonsAntGame
    parental_name = "board"
    colormap = matplotlib.cm.viridis
    scaling = 10
    x_offset = 0
    y_offset = 0
    contents: SparseMatrix

    def __init__(self, game):
        self.game = game
        self.contents = SparseMatrix()
        self.ants = Group()
        self.child_groups = [self.ants]
        self.add_ants(Ant(x=0, y=0, rules_string="rlllr" * 60))
        self.add_ants(Ant(x=0, y=10, rules_string="rlllr" * 60))
        self.add_ants(Ant(x=10, y=0, rules_string="rlllr" * 60))
        self.add_ants(Ant(x=10, y=10, rules_string="rlllr" * 60))
        self.add_ants(Ant(x=5, y=5, rules_string="rllr" * 60))
        super().__init__()

    def add_ants(self, *ants):
        self.add_to_group(*ants, group=self.ants)
        self.calculate_colours()

    def calculate_colours(self):
        """Sample a colormap based on the longest ruleset of child ants"""
        num_colours = max(len(ant.rules) for ant in self.ants)
        samples = numpy.linspace(0, 1, num_colours)
        colours = [tuple(map(int, color[:3])) for color in self.colormap(samples) * 256]
        self.colours = colours

    def get_colour(self, xy: Tuple[int]):
        return self.contents.get(xy, 0)

    def set_colour(self, xy: Tuple[int], colour: int):
        self.contents[xy] = colour

    def draw(self, surface: Surface, debug: bool = False):
        screen_width, screen_height = screen_size = surface.get_size()
        autoscale = False
        for xy, colour_index in self.contents.items():
            sx, sy = self.contents.screen_coords(xy, self.scaling, self.x_offset, self.y_offset)
            if not autoscale and (sx < 0 or sx > screen_width or sy < 0 or sy > screen_height):
                autoscale = True
            colour = self.colours[colour_index]
            pixel = Surface((self.scaling, self.scaling))
            pixel.fill(colour[:3])
            surface.blit(pixel, (sx, sy))
        if autoscale:
            self.scaling, self.x_offset, self.y_offset = self.contents.scale_to_screen(screen_size)
        super().draw(surface, debug)


class Ant(Entity):
    board: Board
    position: tuple
    directions = (
        numpy.array([0, -1]),  # up
        numpy.array([1, 0]),  # right
        numpy.array([0, 1]),  # down
        numpy.array([-1, 0]),  # left
    )

    def __init__(self, x, y, rules_string: str):
        self.position = (x, y)
        self.rules_string = rules_string
        self.rules = self.create_rules(rules_string)
        self.direction_index = 0
        super().__init__()

    @property
    def direction(self):
        return self.directions[self.direction_index]

    def move(self):
        self.position = tuple(self.position + self.direction)

    @classmethod
    def create_rules(cls, rules_string):
        return {
            ii: {
                "next_colour": (ii + 1) % len(rules_string),
                "turn_direction": (1 if char == "r" else -1),
            }
            for ii, char in enumerate(rules_string)
        }

    def update(self):
        # 1) change colour of square
        old_colour = self.board.get_colour(self.position)

        # if the ant doesn't have this colour (number), wrap it by length of
        # this ant's rules
        old_colour %= len(self.rules)
        rule = self.rules[old_colour % len(self.rules)]
        next_colour = rule["next_colour"]
        self.board.set_colour(self.position, next_colour)

        # 2) update direction based on new colour
        turn_direction = self.rules[next_colour]["turn_direction"]
        self.direction_index += turn_direction
        self.direction_index %= len(self.directions)  # wrap

        # 3) move to new square
        self.move()
        return super().update()
