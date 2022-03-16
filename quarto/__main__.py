import sys

import pygame

from quarto.game import QuartoGame


def main():
    game = QuartoGame()
    game.main()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
