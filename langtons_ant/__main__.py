import sys

import pygame

from langtons_ant.game import LangtonsAntGame


def main():
    game = LangtonsAntGame()
    game.main()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
