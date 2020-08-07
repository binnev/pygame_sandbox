import pygame

from volleyball_game.game import VolleyballGame


def main():
    game = VolleyballGame()
    game.main()
    pygame.quit()


if __name__ == "__main__":
    main()
