import string
from typing import NamedTuple


class Square(NamedTuple):
    """Doesn't know anything about the standard chessboard layout (8x8). Should also work for
    other formats."""

    x: int
    y: int

    @classmethod
    def from_str(cls, name: str) -> "Square":
        """
        a1 -> (0, 0)
        h8 -> (7, 7)
        """
        letter, number = name.lower()
        return cls(x=cls.letter_to_x(letter), y=cls.number_to_y(number))

    def to_str(self) -> str:
        """
        (0, 0) -> a1
        (7, 7) -> h8
        """
        x, y = self
        number = self.y_to_number(y)
        letter = self.x_to_letter(x)
        return letter + number

    @staticmethod
    def number_to_y(number: str) -> int:
        return int(number) - 1

    @staticmethod
    def letter_to_x(letter: str) -> int:
        return string.ascii_lowercase.index(letter)

    @staticmethod
    def y_to_number(y: int) -> str:
        return str(y + 1)

    @staticmethod
    def x_to_letter(x: int) -> str:
        return string.ascii_lowercase[x]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.x}, {self.y})"
