import copy
import random
import sys
from collections import deque

import numpy as np
import pygame

from robingame.input import KeyboardInputQueue
from tetris import shapes
from tetris.exceptions import (
    CollisionError,
    ReachedBottomError,
    MaxXError,
    MinXError,
)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
SQUARE_SIZE = 30  # px
COLUMN_COUNT = 10  # squares
ROW_COUNT = 20  # squares
BOARD_WIDTH = COLUMN_COUNT * SQUARE_SIZE
BOARD_HEIGHT = ROW_COUNT * SQUARE_SIZE
BOARD_TOP_LEFT_X = SCREEN_WIDTH // 2 - BOARD_WIDTH // 2
BOARD_TOP_LEFT_Y = SCREEN_HEIGHT // 2 - BOARD_HEIGHT // 2
NEXT_SHAPE_TOP_LEFT_X = BOARD_TOP_LEFT_X + BOARD_WIDTH + 10
NEXT_SHAPE_TOP_LEFT_Y = SCREEN_HEIGHT // 2
MOVEMENT_TIMER = 15


pygame.font.init()


class Colours:
    _colours = {}

    def __init__(self, colours_dict=None):
        if not Colours._colours:
            if not colours_dict:
                colours_dict = {ii: random_colour() for ii in range(1, 10)}
            Colours._colours = colours_dict
        else:
            raise Exception("You can't create a second Colours instance")

    @staticmethod
    def get(key):
        if not Colours._colours:
            Colours()
        return Colours._colours[key]

    @staticmethod
    def random_key():
        if not Colours._colours:
            Colours()
        return random.choice(list(Colours._colours.keys()))

    @staticmethod
    def random_colour():
        if not Colours._colours:
            Colours()
        key = Colours.random_key()
        return Colours.get(key)

    @staticmethod
    def random():
        if not Colours._colours:
            Colours()
        key = Colours.random_key()
        colour = Colours.get(key)
        return key, colour


class Screen:
    """Singleton for getting screen"""

    WIDTH = SCREEN_WIDTH
    HEIGHT = SCREEN_HEIGHT
    SIZE = WIDTH, HEIGHT

    _instance = None

    def __init__(self):
        if Screen._instance is None:
            Screen._instance = pygame.display.set_mode(Screen.SIZE)
        else:
            raise Exception("You can't create a second Screen")

    @staticmethod
    def get():
        if not Screen._instance:
            Screen()
        return Screen._instance


class ShapeQueue:
    _instance = None

    def __init__(self):
        if ShapeQueue._instance is None:
            ShapeQueue._instance = deque()
        else:
            raise Exception("You can't create a second ShapeQueue")

    @classmethod
    def append(cls, value):
        cls._instance.append(value)

    @staticmethod
    def get():
        if not ShapeQueue._instance:
            ShapeQueue()
        return ShapeQueue._instance

    @classmethod
    def next(cls):
        return cls._instance[0]

    @classmethod
    def popleft(cls):
        return cls._instance.popleft()


class Shape:
    def __init__(self, x, y, random_shape=False, colour=None):
        self.x = x
        self.y = y
        self.type = type
        if not random_shape:
            self.array = random.choice(shapes.shapes)
        else:
            self.array = self.generate_random()
        if not colour:
            colour = Colours.random_key()
        self.array = self.array * colour
        print(f"created new Shape: {self.array}")

    def generate_random(self):
        array = np.zeros((5, 5))
        while not np.any(array):
            array = np.array(np.random.uniform(0, 0.8, [3, 3]).round(), dtype=int)
            array = np.pad(array, 1)
        return array

    def check(self, board):
        # assume shapes are always stored in 5x5 arrays
        for y, row in enumerate(self.array):
            for x, item in enumerate(row):
                if not item:  # only do something for full squares
                    continue

                # translate the self.array position to the board position
                board_x = self.x + x - 2
                board_y = self.y + y - 2

                # ignore stuff off the top of the board
                if board_y < 0:
                    continue

                # if shape is outside x bounds
                if 0 > board_x:
                    raise MinXError

                if board_x > COLUMN_COUNT - 1:
                    raise MaxXError

                if board_y > ROW_COUNT - 1:
                    raise ReachedBottomError

                # if square already occupied on board
                if board.array[board_y][board_x]:
                    raise CollisionError("square is already occupied")

    def draw(self, board):
        for y, row in enumerate(self.array):
            for x, item in enumerate(row):
                if not item:  # only do something for full squares
                    continue

                board_x = self.x + x - 2
                board_y = self.y + y - 2

                if board_y >= 0:
                    board.array[board_y][board_x] = item

    def rotate(self, times=1):
        for __ in range(times):
            self.array = np.rot90(self.array)


class Board:
    def __init__(self, rows, columns):
        self.array = np.zeros([ROW_COUNT, COLUMN_COUNT], dtype=int)

    @property
    def complete_lines(self):
        return [ii for ii, row in enumerate(self.array) if all(row)]

    def clear_row(self, row):
        new_row = np.zeros((1, self.width))
        self.array = np.concatenate([new_row, np.delete(self.array, obj=row, axis=0)])

    @property
    def width(self):
        return self.array.shape[1]

    @property
    def height(self):
        return self.array.shape[0]


def random_colour():
    colour = [255, 255, 255]
    while sum(colour) > 400:
        colour = [random.randint(0, 255) for __ in range(3)]
    return colour


def draw_board(board, top_left_x, top_left_y):
    screen = Screen.get()
    height, width = board.array.shape
    pygame.draw.rect(
        screen,
        pygame.color.THECOLORS["darkgray"],
        (top_left_x, top_left_y, width * SQUARE_SIZE, height * SQUARE_SIZE),
    )

    for c in range(width):
        for r in range(height):
            content = board.array[r][c]
            colour = Colours.get(content) if content else pygame.color.THECOLORS["lightgray"]
            pygame.draw.rect(
                screen,
                colour,
                (
                    top_left_x + c * SQUARE_SIZE + 1,
                    top_left_y + r * SQUARE_SIZE + 1,
                    SQUARE_SIZE - 2,
                    SQUARE_SIZE - 2,
                ),
            )


def draw_next_shape_board(array):
    temp_board = Board(0, 0)
    temp_board.array = array
    draw_board(temp_board, NEXT_SHAPE_TOP_LEFT_X, NEXT_SHAPE_TOP_LEFT_Y)


def draw_shape(board, shape):
    new_board = Board(0, 0)
    new_board.array = board.array.copy()
    shape.draw(new_board)
    return new_board


def new_shape():
    return Shape(x=5, y=0)


def new_random_shape():
    return Shape(x=5, y=0, random_shape=True)


def main():
    movement_timer = MOVEMENT_TIMER
    key_handler = KeyboardInputQueue()
    screen = Screen.get()
    myfont = pygame.font.SysFont("monospace", 40)

    board = Board(ROW_COUNT, COLUMN_COUNT)
    shape_queue = ShapeQueue.get()
    shape = new_shape()
    ShapeQueue.append(new_shape())
    clock = pygame.time.Clock()
    score = 0

    iteration = 0
    game_over = False
    while not game_over:
        clock.tick(15)  # sets the FPS. Lower = slower

        # get events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        key_handler.append(pygame.key.get_pressed())

        # move shape
        try:
            if key_handler.get_pressed()[pygame.K_LEFT]:
                try:
                    trial_shape = copy.deepcopy(shape)
                    trial_board = copy.deepcopy(board)
                    trial_shape.x -= 1
                    trial_shape.check(trial_board)
                except (CollisionError, MinXError, IndexError):
                    pass
                else:
                    shape.x -= 1

            if key_handler.get_pressed()[pygame.K_RIGHT]:
                try:
                    trial_shape = copy.deepcopy(shape)
                    trial_board = copy.deepcopy(board)
                    trial_shape.x += 1
                    trial_shape.check(trial_board)
                except (CollisionError, MaxXError, IndexError):
                    pass
                else:
                    shape.x += 1

            if key_handler.get_down()[pygame.K_DOWN]:
                shape.y += 1
                shape.check(board)

            if key_handler.get_pressed()[pygame.K_SPACE]:
                try:
                    trial_shape = copy.deepcopy(shape)
                    trial_board = copy.deepcopy(board)
                    trial_shape.rotate()
                    trial_shape.check(trial_board)
                except (CollisionError, MinXError, MaxXError, IndexError):
                    pass
                else:
                    shape.rotate()

            if iteration % movement_timer == 0:
                shape.y += 1
                shape.check(board)
        except (CollisionError, ReachedBottomError):
            shape.y -= 1
            shape.draw(board)  # fix shape to board
            shape = ShapeQueue.popleft()
            if score < 10:
                ShapeQueue.append(new_shape())
            else:
                ShapeQueue.append(new_random_shape())

        # clear full rows
        for row_number in board.complete_lines:
            board.clear_row(row_number)
            score += 1

        # endgame
        if any(board.array[0]):
            screen.fill([0, 0, 0, 150])
            label = myfont.render("GAME OVER", 1, pygame.color.THECOLORS["white"])
            label_rect = label.get_rect()
            label_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            screen.blit(label, label_rect)
            label = myfont.render(f"SCORE = {score}", 1, pygame.color.THECOLORS["white"])
            label_rect = label.get_rect()
            label_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)
            screen.blit(label, label_rect)
            pygame.display.update()
            pygame.time.wait(3000)
            game_over = True

        # slowly increase the speed with score
        movement_timer = MOVEMENT_TIMER - score // 2

        # draw stuff
        screen.fill(pygame.color.THECOLORS["black"])
        board_to_draw = draw_shape(board, shape)
        draw_board(board_to_draw, BOARD_TOP_LEFT_X, BOARD_TOP_LEFT_Y)
        draw_next_shape_board(ShapeQueue.next().array)
        label = myfont.render(f"SCORE = {score}", 1, pygame.color.THECOLORS["white"])
        screen.blit(label, (40, 10))

        pygame.display.update()
        iteration += 1


if __name__ == "__main__":
    main()
