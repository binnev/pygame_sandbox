import pygame

from base.objects import Game
from dinosaur_jump import conf
from dinosaur_jump.scenes import DinoJumpManager


class DinoJump(Game):
    window_width = conf.WINDOW_WIDTH
    window_height = conf.WINDOW_HEIGHT
    window_caption = "Dino Jump"
    screen_color = (130, 130, 130)

    def __init__(self):
        super().__init__()
        pygame.mouse.set_visible(0)
        self.scenes.add(DinoJumpManager())


if __name__ == "__main__":
    DinoJump().main()
