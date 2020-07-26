import numpy as np

types = ["T", "L", "S", "Z", "I"]

T = np.array([
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0],
])

L = np.array([
    [0, 0, 0, 0, 0],
    [0, 2, 0, 0, 0],
    [0, 2, 2, 2, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
])

S = np.array([
    [0, 0, 0, 0, 0],
    [0, 3, 0, 0, 0],
    [0, 3, 3, 3, 0],
    [0, 0, 0, 3, 0],
    [0, 0, 0, 0, 0],
])

Z = np.array([
    [0, 0, 0, 0, 0],
    [0, 0, 0, 4, 0],
    [0, 4, 4, 4, 0],
    [0, 4, 0, 0, 0],
    [0, 0, 0, 0, 0],
])

I = np.array([
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 5, 5, 5, 5],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
])

