import math

from . import constants
from .body import Body
from .vector import Vector2D


def euclidian_distance(body1: Body, body2: Body) -> float:
    """
    Calculate the Euclidian distance between two objects
    """
    delta_x = abs(body1.x - body2.x)
    delta_y = abs(body1.y - body2.y)
    return math.sqrt(delta_x**2 + delta_y**2)


def attraction_force(body1: Body, body2: Body) -> float:
    """
    Calculate the force of attraction between two bodies according to Newton's law of
    gravitation:
        F = G * (m1 * m2) / R**2
    """
    distance = euclidian_distance(body1, body2)
    return constants.GRAVITATIONAL_CONSTANT * (body1.mass * body2.mass) / distance**2


def newtonian_acceleration(body: Body, force: float) -> float:
    """
    Calculate the acceleration on a body caused by a force, according to Newton's second law of
    motion:
        F = m * a
    or
        a = F / m
    """
    return force / body.mass


def gravitational_attraction(body1: Body, body2: Body):
    """
    1. Calculate the gravitational attraction force between two objects
    2. Calculate the resulting acceleration for each object based on its mass
    3. Calculate the x/y components of the acceleration for each object
    4. Adjust each objects u/v according to its acceleration
    """

    # 1
    force = attraction_force(body1, body2)
    # 2
    acc1 = newtonian_acceleration(body1, force)
    acc2 = newtonian_acceleration(body2, force)
    # 3
    dx = body2.x - body1.x
    dy = body2.y - body1.y
    vector = Vector2D(dx, dy)  # vector from body1 to body2
    unit = vector.unit()
    acc1_x = acc1 * unit.dx
    acc1_y = acc1 * unit.dy
    vector = vector.reverse()
    unit = vector.unit()
    acc2_x = acc2 * unit.dx
    acc2_y = acc2 * unit.dy

    # 4
    body1.u += acc1_x
    body1.v += acc1_y
    body2.u += acc2_x
    body2.v += acc2_y
