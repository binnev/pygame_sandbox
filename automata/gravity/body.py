from dataclasses import dataclass


@dataclass
class Body:
    mass: float  # kg
    radius: float  # m
    u: float = 0  # m/s
    v: float = 0  # m/s
