import sys

import numpy as np
import pygame

from platformer.objects.keyhandlers import KeyHandler
from tetris import shapes

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
SQUARE_SIZE = 30  # px
COLUMN_COUNT = 10  # squares
ROW_COUNT = 20  # squares
BOARD_WIDTH = COLUMN_COUNT * SQUARE_SIZE
BOARD_HEIGHT = ROW_COUNT * SQUARE_SIZE
BOARD_TOP_LEFT_X = SCREEN_WIDTH / 2 - BOARD_WIDTH / 2
BOARD_TOP_LEFT_Y = SCREEN_HEIGHT / 2 - BOARD_HEIGHT / 2

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

    def draw(self, board):
        # assume shapes are always stored in 5x5 arrays
        for y, row in enumerate(self.array):
            for x, item in enumerate(row):
                if item:  # only do something for full squares
                    # if square already occupied, raise exception
                    if board[self.y + y - 2][self.x + x - 2]:
                        raise Exception("square is already occupied")

                    board[self.y + y - 2][self.x + x - 2] = item

    def rotate(self):
        self.array = np.rot90(self.array)


def create_board():
    return np.zeros([ROW_COUNT, COLUMN_COUNT], dtype=int)


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
            content = board[r][c]
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
    board = board.copy()
    shape.draw(board)
    return board


def main():
    key_handler = KeyHandler(queue_length=5)
    screen = Screen.get()

    board = create_board()
    shape = Shape(type="T", x=0, y=0)

    print(shape.array)

    game_over = False
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            keys = pygame.key.get_pressed()
            key_handler.update(keys)
            pressed = key_handler.get_pressed()

            if pressed[pygame.K_LEFT]:
                print("key")
                shape.x -= 1
            if pressed[pygame.K_RIGHT]:
                print("key")
                shape.x += 1
            if pressed[pygame.K_UP]:
                print("key")
                shape.y -= 1
            if pressed[pygame.K_DOWN]:
                print("key")
                shape.y += 1
            if pressed[pygame.K_SPACE]:
                print("rotate!")
                shape.rotate()


        # draw stuff
        screen.fill(pygame.color.THECOLORS["black"])
        draw_environment()
        board_to_draw = draw_shape(board, shape)
        draw_board(board_to_draw)
        pygame.display.update()


if __name__ == "__main__":
    main()
