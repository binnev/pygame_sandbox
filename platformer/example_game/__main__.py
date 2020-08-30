import pygame

from platformer.example_game.game import ExampleGame


def main():
    game = ExampleGame()
    game.main()
    pygame.quit()


if __name__ == "__main__":
    main()
