import sys

import pygame

from maze_solver.game import MazeSolverGame


def main():
    game = MazeSolverGame()
    game.main()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
