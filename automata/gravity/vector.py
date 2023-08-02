import math

from typing import NamedTuple


class Vector2D(NamedTuple):
    dx: float
    dy: float

    def magnitude(self) -> float:
        dx, dy = self
        return math.sqrt(dx**2 + dy**2)

    def unit(self) -> "Vector2D":
        mag = self.magnitude()
        return Vector2D(
            self.dx / mag,
            self.dy / mag,
        )

    def reverse(self) -> "Vector2D":
        return Vector2D(-self.dx, -self.dy)
