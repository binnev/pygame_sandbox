from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from .board import ChessBoard

WHITE = "white"
BLACK = "black"


class Piece:
    team: str  # "white" or "black"
    letter: str  # "k" for king
    board: "ChessBoard"
    square: Tuple[int, int]

    def __init__(self, team):
        self.team = team

    def __str__(self):
        return self.letter.upper() if self.team == WHITE else self.letter.lower()

    @property
    def moves_unfiltered(self):
        """Set of squares this piece could move to if nothing is blocking the way"""
        return set()

    @property
    def moves(self) -> set:
        """Set of squares this piece could move to, taking into account obstructions and board
        edges"""
        return {
            move
            for move in self.moves_unfiltered
            if move in self.board.squares  # respect board limits
            and (
                self.board.contents.get(move) is None  # empty squares
                or self.board.contents.get(move).team != self.team  # only capture enemies
            )
        }

    @property
    def square(self):
        """Coordinates of self on board"""
        return self.board.locate(self)


class King(Piece):
    letter = "k"

    @property
    def moves_unfiltered(self):
        x, y = self.square
        return {
            (x - 1, y - 1),
            (x - 1, y),
            (x - 1, y + 1),
            (x, y - 1),
            (x, y + 1),
            (x + 1, y - 1),
            (x + 1, y),
            (x + 1, y + 1),
        }


class Queen(Piece):
    letter = "q"


class Bishop(Piece):
    letter = "b"


class Knight(Piece):
    letter = "n"

    @property
    def moves_unfiltered(self) -> set:
        x, y = self.square
        return {
            (x + 1, y + 2),
            (x + 2, y + 1),
            (x + 2, y - 1),
            (x + 1, y - 2),
            (x - 1, y - 2),
            (x - 2, y - 1),
            (x - 2, y + 1),
            (x - 1, y + 2),
        }


class Rook(Piece):
    letter = "r"


class Pawn(Piece):
    letter = "p"
