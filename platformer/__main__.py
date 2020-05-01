# ======= this block has to come first to preserve the pygame loading order ==============
import pygame

pygame.init()
window = pygame.display.set_mode((500, 500))
pygame.display.set_caption("")
# ========================================================================================

from platformer.objects.game import Game


def main():
    game = Game(window)
    game.main()
    pygame.quit()


if __name__ == "__main__":
    main()
