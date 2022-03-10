from typing import NamedTuple, TYPE_CHECKING

from chess.constants import PieceTypes

if TYPE_CHECKING:
    from chess.engine.classes.piece import Piece
    from chess.engine.classes.square import Square


class Move(NamedTuple):
    """Basically a diff between two Positions"""

    origin: "Square"
    destination: "Square"
    piece: "Piece"
    captured_piece: "Piece" = None
    captured_piece_square: "Square" = None
    promote_to: PieceTypes = None
    extra_move: "Move" = None
