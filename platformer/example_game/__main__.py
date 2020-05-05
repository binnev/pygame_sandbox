# ======= this block has to come first to preserve the pygame loading order ==============
import pygame

from platformer.example_game.conf import SCREEN_WIDTH, SCREEN_HEIGHT

pygame.init()
pygame.font.init()
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("")
# ========================================================================================
from platformer.example_game.game import ExampleGame


def main():
    game = ExampleGame(window, fps=60)
    game.main()
    pygame.quit()


if __name__ == "__main__":
    main()
