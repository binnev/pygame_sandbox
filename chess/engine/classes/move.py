from typing import NamedTuple

from chess.engine.classes.square import Square


class Move(NamedTuple):
    origin: Square
    destination: Square
