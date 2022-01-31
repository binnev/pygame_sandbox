from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .board import ChessBoard

WHITE = "white"
BLACK = "black"


class Piece:
    team: str  # "white" or "black"
    letter: str  # "k" for king
    board: "ChessBoard"

    def __init__(self, team):
        self.team = team

    def __str__(self):
        return self.letter.upper() if self.team == WHITE else self.letter.lower()


class King(Piece):
    letter = "k"


class Queen(Piece):
    letter = "q"
