import math

import numpy
from pygame import Rect
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

        # 3 collisions
        while self.do_collisions():
            pass

    def do_collisions(self) -> bool:
        """
        fixme: refactor
        Do one round of collision processing.
        Return True if collisions were processed.
        """
        for xy1, body1 in self.contents.items():
            for xy2, body2 in self.contents.items():
                if body1 is body2:
                    continue  # bodies can't affect themselves

                dist = physics.euclidian_distance(xy1, xy2)
                if dist < body1.radius + body2.radius:
                    m1, m2 = body1.mass, body2.mass
                    x1, y1 = xy1
                    x2, y2 = xy2
                    new_x = (x1 * m1 + x2 * m2) / (m1 + m2)
                    new_y = (y1 * m1 + y2 * m2) / (m1 + m2)
                    new_u = (m1 * body1.u + m2 * body2.u) / (m1 + m2)
                    new_v = (m1 * body1.v + m2 * body2.v) / (m1 + m2)
                    new_radius = numpy.sqrt(body1.radius**2 + body2.radius**2)
                    new_body = Body(
                        mass=body1.mass + body2.mass,
                        radius=new_radius,
                        u=new_u,
                        v=new_v,
                    )
                    self.contents.pop((x1, y1))
                    self.contents.pop((x2, y2))
                    self.contents[(new_x, new_y)] = new_body
                    return True
        return False

    def add_body(self, x: float, y: float, body: Body):
        self.contents[(x, y)] = body
