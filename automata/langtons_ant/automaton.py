from dataclasses import dataclass

import numpy
from robingame.utils import SparseMatrix, Coord


@dataclass
class Ant:
    ruleset: str
    xy: Coord
    facing: int
    directions = (
        numpy.array([0, -1]),  # up
        numpy.array([1, 0]),  # right
        numpy.array([0, 1]),  # down
        numpy.array([-1, 0]),  # left
    )

    def iterate(self, contents: SparseMatrix):
        # increment colour
        old_colour = contents.get(self.xy, 0)
        old_colour %= len(self.ruleset)
        next_colour = old_colour + 1
        next_colour %= len(self.ruleset)

        # update grid with new colour
        contents[self.xy] = next_colour

        # turn
        turn_direction = 1 if self.ruleset[next_colour] == "r" else -1
        self.facing += turn_direction
        self.facing %= len(self.directions)

        # move to next square
        self.xy = tuple(self.directions[self.facing] + self.xy)


class LangtonsAntAutomaton:
    """Implements Automaton"""

    contents: SparseMatrix

    # other state / game rules also stored on this class
    ants: list[Ant]

    def __init__(self, contents=None, ants=None):
        self.contents = contents or SparseMatrix()
        self.ants = ants or []

    def iterate(self):
        for ant in self.ants:
            ant.iterate(self.contents)

    def add_ant(self, xy: Coord, ruleset: str, facing: int):
        ant = Ant(ruleset=ruleset, xy=xy, facing=facing)
        self.ants.append(ant)
