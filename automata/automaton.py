from typing import Protocol, runtime_checkable

from robingame.utils import SparseMatrix


@runtime_checkable
class Automaton(Protocol):
    """
    Stores game state (in SparseMatrix and possibly other stuff too).
    Implements iteration of the game rules.
    """

    # this needs to be exposed because other parts of the code want to access it
    contents: SparseMatrix

    def iterate(self):
        """Perform 1 iteration of the game rules."""
