import sys

import numpy as np
import pygame

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
                    BOARD_TOP_LEFT_X + c * SQUARE_SIZE +1,
                    BOARD_TOP_LEFT_Y + r * SQUARE_SIZE +1,
                    SQUARE_SIZE-2,
                    SQUARE_SIZE-2,
                ),
            )


def main():

    screen = Screen.get()

    board = create_board()
    board[1][1] = 1
    board[2][2] = 2
    board[3][3] = 3
    board[4][4] = 4
    board[5][5] = 5
    board[6][6] = 6
    print(board)
    draw_board(board)

    game_over = False
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill(pygame.color.THECOLORS["black"])

        draw_environment()
        draw_board(board)
        pygame.display.update()


if __name__ == "__main__":
    main()
