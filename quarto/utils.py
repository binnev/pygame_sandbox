import math
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from quarto.objects import Piece


def common_attribute(row: List["Piece"]) -> str | None:
    for attribute in ["tall", "hollow", "square", "black"]:
        if all(getattr(p, attribute) for p in row):
            return attribute
        if all(not getattr(p, attribute) for p in row):
            return f"not {attribute}"


# for row in [
#     (Piece(True, True, True, True), Piece(False, False, False, False)),
#     (Piece(True, True, True, True), Piece(False, False, False, True)),
#     (Piece(True, True, True, True), Piece(True, False, False, True)),
#     (Piece(False, True, True, True), Piece(True, False, False, True)),
#     (Piece(False, True, True, True), Piece(True, False, False, False)),
#     (Piece(False, True, False, True), Piece(True, False, False, False)),
# ]:
#     print(common_attribute(row))


def distance(coords1, coords2):
    x1, y1 = coords1
    x2, y2 = coords2
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx**2 + dy**2)
