import sys

import pygame

from automata.advent_of_code_day9.game import AdventOfCodeDay9Game


def main():
    game = AdventOfCodeDay9Game()
    game.main()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
