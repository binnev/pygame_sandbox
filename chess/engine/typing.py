from collections import namedtuple
from typing import NamedTuple

Square = namedtuple("Square", "x y")


class Move(NamedTuple):
    origin: Square
    destination: Square
