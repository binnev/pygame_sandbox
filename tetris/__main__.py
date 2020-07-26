import random
import sys

import numpy as np
import pygame

from platformer.objects.keyhandlers import KeyHandler
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
BOARD_TOP_LEFT_X = SCREEN_WIDTH / 2 - BOARD_WIDTH / 2
BOARD_TOP_LEFT_Y = SCREEN_HEIGHT / 2 - BOARD_HEIGHT / 2

MOVEMENT_TIMER = 15

COLOURS = {
    0: pygame.color.THECOLORS["lightgray"],
    1: pygame.color.THECOLORS["cyan"],
    2: pygame.color.THECOLORS["blue"],
    3: pygame.color.THECOLORS["green"],
    4: pygame.color.THECOLORS["yellow"],
    5: pygame.color.THECOLORS["purple"],
}

pygame.font.init()


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


class Shape:
    def __init__(self, type, x, y):
        self.type = type
        self.array = getattr(shapes, type)
        self.x = x
        self.y = y

    def pad(self, board):
        """Return an empty board with self on it"""
        board = np.zeros(board.shape)
        self.draw(board)
        return board

    def check(self, board):
        # assume shapes are always stored in 5x5 arrays
        for y, row in enumerate(self.array):
            for x, item in enumerate(row):
                if not item:  # only do something for full squares
                    continue

                # translate the self.array position to the board position
                board_x = self.x + x - 2
                board_y = self.y + y - 2

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

    def rotate(self):
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


def draw_environment():
    screen = Screen.get()
    pygame.draw.rect(
        screen,
        pygame.color.THECOLORS["darkgray"],
        (BOARD_TOP_LEFT_X, BOARD_TOP_LEFT_Y, BOARD_WIDTH, BOARD_HEIGHT),
    )


def draw_board(board):
    screen = Screen.get()
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            content = board.array[r][c]
            pygame.draw.rect(
                screen,
                COLOURS.get(content, pygame.color.THECOLORS["red"]),
                (
                    BOARD_TOP_LEFT_X + c * SQUARE_SIZE + 1,
                    BOARD_TOP_LEFT_Y + r * SQUARE_SIZE + 1,
                    SQUARE_SIZE - 2,
                    SQUARE_SIZE - 2,
                ),
            )


def draw_shape(board, shape):
    new_board = Board(0, 0)
    new_board.array = board.array.copy()
    shape.draw(new_board)
    return new_board


def new_shape():
    shape_type = random.choice(shapes.types)
    return Shape(type=shape_type, x=5, y=0)


def main():
    movement_timer = MOVEMENT_TIMER
    key_handler = KeyHandler(queue_length=5)
    screen = Screen.get()
    myfont = pygame.font.SysFont("monospace", 40)

    board = Board(ROW_COUNT, COLUMN_COUNT)
    shape = new_shape()
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
        key_handler.update(pygame.key.get_pressed())

        # move shape
        try:
            if key_handler.get_pressed()[pygame.K_LEFT]:
                try:
                    shape.x -= 1
                    shape.check(board)
                except (CollisionError, MinXError):
                    shape.x += 1
            if key_handler.get_pressed()[pygame.K_RIGHT]:
                try:
                    shape.x += 1
                    shape.check(board)
                except (CollisionError, MaxXError):
                    shape.x -= 1
            if key_handler.get_down()[pygame.K_DOWN]:
                shape.y += 1
                shape.check(board)
            if key_handler.get_pressed()[pygame.K_SPACE]:
                shape.rotate()
            if iteration % movement_timer == 0:
                shape.y += 1
                shape.check(board)
        except (CollisionError, ReachedBottomError):
            shape.y -= 1
            shape.draw(board)  # fix shape to board
            shape = new_shape()

        # clear full rows
        for row_number in board.complete_lines:
            board.clear_row(row_number)
            score += 1

        # todo: show next shape
        # todo: random shaped blocks...

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
        movement_timer = MOVEMENT_TIMER - score // 1

        # draw stuff
        screen.fill(pygame.color.THECOLORS["black"])
        draw_environment()
        board_to_draw = draw_shape(board, shape)
        draw_board(board_to_draw)
        label = myfont.render(f"SCORE = {score}", 1, pygame.color.THECOLORS["white"])
        screen.blit(label, (40, 10))

        pygame.display.update()
        iteration += 1


if __name__ == "__main__":
    main()
