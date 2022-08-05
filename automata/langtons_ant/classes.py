from typing import Tuple

import matplotlib
import numpy
from pygame.surface import Surface

from automata.langtons_ant.game import LangtonsAntGame
from automata.utils import SparseMatrix
from base.objects import Entity, Group


class Board(Entity):
    """The board on which the ants crawl"""

    game: LangtonsAntGame
    parental_name = "board"
    colormap = matplotlib.cm.viridis
    scaling = 15
    contents: SparseMatrix

    def __init__(self, game):
        self.max_x = 0
        self.min_x = 0
        self.max_y = 0
        self.min_y = 0
        self.game = game
        self.contents = SparseMatrix()
        self.ants = Group()
        self.child_groups = [self.ants]
        self.add_ants(Ant(x=0, y=0, rules_string="rl"))
        super().__init__()
        self.calculate_screen_mapping()

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

    def map_self_to_screen(self, x, y):
        screen_x = self.screen_origin_x + (x * self.scaling)
        screen_y = self.screen_origin_y + (y * self.scaling)
        return screen_x, screen_y

    def calculate_screen_mapping(self):
        self.screen_origin_x = (self.game.window_width / 2) - self.scaling * (
            self.contents.width / 2 + self.contents.xlim[0]
        )
        self.screen_origin_y = (self.game.window_height / 2) - self.scaling * (
            self.contents.height / 2 + self.contents.ylim[0]
        )

    def draw(self, surface: Surface, debug: bool = False):
        xlim = self.contents.xlim
        ylim = self.contents.ylim
        screen_x_min, screen_y_min = self.map_self_to_screen(xlim[0], ylim[0])
        screen_x_max, screen_y_max = self.map_self_to_screen(xlim[1], ylim[1])
        if (
            screen_x_max > self.game.window_width
            or screen_x_min < 0
            or screen_y_max > self.game.window_height
            or screen_y_min < 0
        ):
            self.scaling = max([1, self.scaling - 1])
            self.calculate_screen_mapping()

        for (x, y), colour_index in self.contents.items():
            pixel = Surface((self.scaling, self.scaling))
            colour = self.colours[colour_index]
            pixel.fill(colour[:3])
            screen_x, screen_y = self.map_self_to_screen(x, y)
            surface.blit(pixel, (screen_x, screen_y))

        super().draw(surface, debug)

    # def map_mouse_to_self(self, x_mouse, y_mouse):
    #     x_self = linear_map(x_mouse, (0, self.game.window_width), self.xlim)
    #     y_self = linear_map(y_mouse, (0, self.game.window_height), self.ylim)
    #     return x_self, y_self
    #
    # def handle_click(self, mouse_xy):
    #     x, y = self.map_mouse_to_self(*mouse_xy)
    #     # x, y =
    #     self.add_ants(Ant(x, y, rules_string="rrrlr"))


class Ant(Entity):
    board: Board
    position: tuple
    directions = (
        numpy.array([-1, 0]),  # up
        numpy.array([0, 1]),  # right
        numpy.array([1, 0]),  # down
        numpy.array([0, -1]),  # left
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
