import sys

import pygame

from fighting_game.game import FightingGame


def main():
    game = FightingGame()
    game.main()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
