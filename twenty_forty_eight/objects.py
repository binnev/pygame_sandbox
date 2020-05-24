import random

import numpy as np
import pygame

"""
TODO: 
[ ] make object oriented version. The current functions just deal with lists of numbers. 
    It's too abstract. How will the algorithm look for the object oriented version? Need to 
    consider how the objects will animate. It won't be as simple as doing sum(a, b).  
"""


def slide_row_left(row: [int]):
    # if there are no entries in the row, return the unchanged row
    if set(row) == {0}:
        return row
    length = len(row)
    modified = [item for item in row if item]  # filter out zeros
    modified = add_pairs(modified)  # resolve collisions
    modified += [0] * (length - len(modified))  # pad with zeros
    return modified


def add_pairs(row):
    """This function expects a list of just values; no zeros"""
    if 0 in row:
        raise Exception("no zeros allowed")
    # base case
    if len(row) < 2:
        return row
    # recursive case
    a, b = row[0], row[1]
    if a == b:
        # if first two are equal, sum and process rest of row
        return [a + b] + add_pairs(row[2:])
    else:
        # if first two are not equal, skip first and process rest of row
        return [a] + add_pairs(row[1:])


def slide_left(grid):
    for i, row in enumerate(grid):
        grid[i] = slide_row_left(row)
    return grid


class Board:
    def __init__(self, size):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self.previous_grid = self.grid.copy()
        for __ in range(2):
            self.add_random_entry()

    def add_random_entry(self):
        if self.is_full():
            raise Exception("board is full!")
        # try a random space
        x = random.randint(0, self.size - 1)
        y = random.randint(0, self.size - 1)
        while self.grid[x][y]:  # is occupied
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
        self.grid[x][y] = 2

    def update(self, keys):
        self.previous_grid = self.grid.copy()
        self.handle_keypresses(keys)

    def has_changed(self):
        return not (self.grid == self.previous_grid).all()

    def handle_keypresses(self, keys):
        if keys[pygame.K_RIGHT]:
            print("right key pressed")
            self.slide_right()
        if keys[pygame.K_LEFT]:
            print("left key pressed")
            self.slide_left()
        if keys[pygame.K_UP]:
            print("up key pressed")
            self.slide_up()
        if keys[pygame.K_DOWN]:
            print("down key pressed")
            self.slide_down()

    def slide_left(self):
        self.grid = slide_left(self.grid)

    def slide_right(self):
        temp_grid = np.rot90(self.grid, 2)
        temp_grid = slide_left(temp_grid)
        self.grid = np.rot90(temp_grid, 2)

    def slide_up(self):
        temp_grid = np.rot90(self.grid)
        temp_grid = slide_left(temp_grid)
        self.grid = np.rot90(temp_grid, 3)

    def slide_down(self):
        temp_grid = np.rot90(self.grid, 3)
        temp_grid = slide_left(temp_grid)
        self.grid = np.rot90(temp_grid)

    def is_full(self):
        return 0 not in self.grid


class Block:
    def __init__(self, value):
        self.value = value
