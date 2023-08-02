from dataclasses import dataclass


@dataclass
class Body:
    x: float  # m
    y: float  # m
    mass: float  # kg
    radius: float  # m
    u: float = 0  # m/s
    v: float = 0  # m/s
