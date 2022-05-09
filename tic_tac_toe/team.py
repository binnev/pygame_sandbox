from dataclasses import dataclass

from tic_tac_toe.constants import O, X


@dataclass
class Team:
    """Links a symbol/name like "O" or "white" to a generic boolean team marker that can be used
    by algorithms like minimax with no knowledge of the game it's playing."""

    symbol: str
    boolean: bool  # used for game-independent algorithms like minimax

    @property
    def win_value(self):
        """In minimax, team True wins with positive scores, and team False wins with negative
        scores."""
        return 1 if self.boolean else -1


TEAM_O = Team(O, True)
TEAM_X = Team(X, False)
