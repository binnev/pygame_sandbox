import sys

import pygame

from fighting_game.game import FightingGame


def main():
    game = FightingGame()
    try:
        game.main()
    except Exception:
        main()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()