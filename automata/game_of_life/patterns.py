import numpy

from base.utils import SparseMatrix


def load_pattern(pattern: str, shift: tuple[int, int] = (0, 0)) -> SparseMatrix:
    arr = numpy.array(
        [(x, y) for y, row in enumerate(pattern) for x, value in enumerate(row) if value]
    )
    arr += shift
    arr = [tuple(item) for item in arr]
    return SparseMatrix({coord: True for coord in arr})


BLOCK = """
xxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxx
"""
GLIDER = """
.x.
..x
xxx
"""

LIGHTWEIGHT_SPACESHIP = """
.xxxx
x...x
....x
x..x.
"""

MEDIUM_SPACESHIP = """
.xxxxx
x....x
.....x
x...x.
..x...
"""

HEAVY_SPACESHIP = """
.xxxxxx
x.....x
......x
x....x.
..xx...
"""
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

ACORN = """
.x.....
...x...
xx..xxx
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
