import sys

import pygame

from automata.advent_of_code.game import AdventOfCodeGame


def main():
    game = AdventOfCodeGame()
    game.main()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
