from typing import Set, NamedTuple, TYPE_CHECKING

from chess.constants import (
    WHITE,
    BLACK,
    PieceTypes,
    Teams,
    LETTER_TO_PIECE,
    PIECE_TO_SYMBOL,
    PIECE_TO_LETTER,
)
from chess.engine.classes.square import Square
from chess.engine.utils import get_squares

if TYPE_CHECKING:
    from chess.engine.classes.position import Position


class Piece(NamedTuple):
    """Knows its type and team. Does not know its location (square)"""

    team: Teams
    type: PieceTypes

    def __str__(self):
        letter = PIECE_TO_LETTER[self.type]
        return letter.upper() if self.team == WHITE else letter.lower()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.team} {self.type})"

    def symbol(self):
        return PIECE_TO_SYMBOL[self.team][self.type]

    @classmethod
    def from_letter(cls, letter: str):
        """Note: limited to traditional black/white only"""
        team = WHITE if letter.isupper() else BLACK
        letter = letter.lower()
        piece_type = LETTER_TO_PIECE[letter]
        return cls(team, piece_type)

    @property
    def letter(self):
        letter = PIECE_TO_LETTER[self.type]
        return letter.upper() if self.team == WHITE else letter.lower()

    def get_squares(self, current_square: Square, position: "Position") -> Set[Square]:
        return get_squares(current_square=current_square, position=position)

