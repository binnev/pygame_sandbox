import numpy
from robingame.utils import SparseMatrix

from . import physics
from .body import Body

CoordFloat2D = tuple[float, float]


class GravityAutomaton:
    contents: SparseMatrix[CoordFloat2D:Body]

    def __init__(self):
        self.contents = SparseMatrix()

    def iterate(self):
        """
        1. Apply the rules of gravitation attraction between each pair of objects
        2. Move every object according to the laws of motion
        """
        # 1
        for xy1, body1 in self.contents.items():
            for xy2, body2 in self.contents.items():
                if body1 is body2:
                    continue  # bodies can't affect themselves
                physics.gravitational_attraction(body1, xy1, body2, xy2)

        # 2
        new = SparseMatrix()
        for (x, y), body in self.contents.items():
            x += body.u
            y += body.v
            new[(x, y)] = body
        self.contents = new

    def add_body(self, x: float, y: float, body: Body):
        self.contents[(x, y)] = body
