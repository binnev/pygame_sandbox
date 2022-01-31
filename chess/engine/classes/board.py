import string
from typing import Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .piece import Piece


class ChessBoard:
    contents: Dict[Tuple[int, int], "Piece"]
    height: int = 8
    width: int = 8

    def __init__(self, height=None, width=None):
        self.contents = dict()
        self.height = height if height else self.height
        self.width = width if width else self.width

    def add_piece(self, square: Tuple[int, int], piece):
        self.contents[square] = piece

    def remove_piece(self, square: Tuple[int, int]):
        del self.contents[square]

    def move_piece(self, square1, square2):
        self.contents[square2] = self.contents.pop(square1)

    def __str__(self):
        xs = [x for x, y in self.contents]
        ys = [-y for x, y in self.contents]
        string = ""
        for y in range(min(ys), max(ys) + 1):
            for x in range(min(xs), max(xs) + 1):
                string += str(self.contents.get((x, -y), "."))
            string += "\n"
        return string

    def square_coords(self, name: str):
        """
        a1 -> (0, 0)
        h8 -> (7, 7)
        """
        name = name.lower()
        x, y = name
        y = int(y) - 1
        x = string.ascii_lowercase.index(x)
        return (x, y)

    def square_name(self, square: Tuple[int, int]):
        """
        (0, 0) -> a1
        (7, 7) -> h8
        """
        x, y = square
        y = str(y + 1)
        x = string.ascii_lowercase[x]
        return x + y
