from collections import namedtuple
from dataclasses import dataclass
from typing import NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    from chess.engine.classes.piece import Piece

Square = namedtuple("Square", "x y")


@dataclass
class Move:
    origin: Square
    destination: Square
    captured_piece: "Piece" = None

    def do(self):
        ...

    def undo(self):
        ...