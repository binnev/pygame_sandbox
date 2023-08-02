import numpy
from robingame.utils import SparseMatrix

from . import physics
from .body import Body

CoordFloat2D = tuple[float, float]


class GravityAutomaton:
    bodies: list[Body]

    def __init__(self):
        self.bodies = []
        self.contents = SparseMatrix()

    def iterate(self):
        """
        1. Apply the rules of gravitation attraction between each pair of objects
        2. Move every object according to the laws of motion
        """
        # 1
        for body1 in self.bodies:
            for body2 in self.bodies:
                if body1 is body2:
                    continue  # bodies can't affect themselves
                physics.gravitational_attraction(body1, body2)

        # 2
        for body in self.bodies:
            body.x += body.u
            body.y += body.v

    def add_body(self, body: Body):
        self.bodies.append(body)