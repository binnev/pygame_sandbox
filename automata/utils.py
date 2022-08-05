Coord = tuple[int, int]


def unzip(zipped):
    return tuple(zip(*zipped))


class SparseMatrix(dict):
    """
    Dictionary of the form {(x, y): value}. Can be used to simulate an infinite grid.
    """

    @property
    def xlim(self):
        xs = [x for x, y in self.keys()] or [0]
        return min(xs), max(xs)

    @property
    def ylim(self):
        ys = [y for x, y in self.keys()] or [0]
        return min(ys), max(ys)

    @property
    def height(self):
        ylim = self.ylim
        return ylim[1] - ylim[0]

    @property
    def width(self):
        xlim = self.xlim
        return xlim[1] - xlim[0]

    @property
    def size(self) -> (int, int):
        xs, ys = unzip(self.keys()) or ([0], [0])
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        return width, height

    def copy(self) -> "SparseMatrix":
        return SparseMatrix(super().copy())

