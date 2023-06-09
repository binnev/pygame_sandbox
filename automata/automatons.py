from dataclasses import dataclass
from typing import Protocol, runtime_checkable, NamedTuple

import numpy
from robingame.utils import SparseMatrix, Coord

from automata.game_of_life import threshold


@runtime_checkable
class Automaton(Protocol):
    """
    Stores game state (in SparseMatrix and possibly other stuff too).
    Implements iteration of the game rules.
    """

    # this needs to be exposed because other parts of the code want to access it
    contents: SparseMatrix

    def iterate(self):
        ...


class GameOfLifeAutomaton:
    """Implements Automaton"""

    contents: SparseMatrix

    # other state / game rules also stored on this class
    overpopulation_threshold: int
    underpopulation_threshold: int
    reproduction_threshold: int

    def __init__(
        self,
        contents=None,
        underpopulation_threshold=threshold.UNDERPOPULATION,
        overpopulation_threshold=threshold.OVERPOPULATION,
        reproduction_threshold=threshold.REPRODUCTION,
    ):
        self.contents = contents or SparseMatrix()
        self.underpopulation_threshold = underpopulation_threshold
        self.overpopulation_threshold = overpopulation_threshold
        self.reproduction_threshold = reproduction_threshold

    def iterate(self):
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
        left = x - 1
        right = x + 1
        up = y - 1
        down = y + 1
        return (
            (left, up),
            (left, y),
            (left, down),
            (x, up),
            (x, down),
            (right, up),
            (right, y),
            (right, down),
        )


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
