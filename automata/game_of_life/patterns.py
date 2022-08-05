import numpy

from base.utils import SparseMatrix


def load_pattern(pattern: str) -> SparseMatrix:
    return SparseMatrix(
        {(x, y): True for y, row in enumerate(pattern) for x, value in enumerate(row) if value}
    )


INFINITE_GROWER = """
XXX.X
X....
...XX
.XX.X
X.X.X
"""

INFINITE_GROWER2 = """
......x.
....x.xx
....x.x.
....x...
..x.....
x.x.....
"""

R_PENTOMINO = """
.XX
XX.
.X.
"""

DIE_HARD = """
......X.
XX......
.X...XXX
"""
l = locals().copy()
for k, v in l.items():
    if isinstance(k, str) and k.isupper():
        strings = list(filter(None, v.split("\n")))
        arr = numpy.array([[int(char != ".") for char in row] for row in strings])
        locals()[k] = arr

INFINITE_GROWER_1HIGH = """
xxxxxxxx.xxxxx...xxx......xxxxxxx.xxxxx
"""
