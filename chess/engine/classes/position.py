from typing import Optional, Set

from chess.constants import WHITE, Teams
from chess.engine.classes.move import Move
from chess.engine.classes.piece import Piece
from chess.engine.classes.square import Square
from chess.notation import parse_fen_string, parse_fen_position


class Position(dict):
    """
    Represents the position of the pieces on the chessboard.
    Not bounded to the normal 8x8 grid.
    Mutable.
    """

    width: int = 8
    height: int = 8

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.squares = tuple(Square(x, y) for y in range(self.height) for x in range(self.width))

    def get(self, square: Square, default=None) -> Optional[Piece]:
        return super().get(square, default)

    def add(self, piece: Piece, square: Square):
        self[square] = piece

    def do_move(self, move: Move):
        """Apply the move, mutating the position in place. """
        self.pop(move.origin)
        if move.captured_piece:
            self.pop(move.captured_piece_square)
        piece = Piece(move.piece.team, move.promote_to) if move.promote_to else move.piece
        self.add(piece, move.destination)
        if move.extra_move:
            self.do_move(move.extra_move)

    def __str__(self, V_SEP="\n", H_SEP=" ") -> str:
        xs = range(self.width)
        ys = range(0, -self.height, -1)
        return V_SEP.join(
            H_SEP.join(str(self.get(Square(x, -y), ".")) for x in range(min(xs), max(xs) + 1))
            for y in range(min(ys), max(ys) + 1)
        )

    def pawn_starting_squares(self, team) -> Set[Square]:
        return (
            {Square(x, 1) for x in range(self.width)}
            if team == WHITE
            else {Square(x, self.height - 2) for x in range(self.width)}
        )

    def is_pawn_starting_square(self, square: Square, team: Teams) -> bool:
        return square in self.pawn_starting_squares(team)

    @classmethod
    def from_fen(cls, string):
        position, *_ = parse_fen_string(string)
        pieces = parse_fen_position(position)
        return cls(pieces)