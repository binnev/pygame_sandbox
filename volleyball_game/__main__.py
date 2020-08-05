import pygame

from volleyball_game.game import VolleyballGame


def main():
    pygame.init()
    window = pygame.display.set_mode((500, 500))
    pygame.display.set_caption("")

    game = VolleyballGame(window, fps=60)
    game.main()
    pygame.quit()


if __name__ == "__main__":
    main()
