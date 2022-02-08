import pygame
import sys
from chess.gui.game import ChessGame


def main():
    game = ChessGame()
    game.main()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
