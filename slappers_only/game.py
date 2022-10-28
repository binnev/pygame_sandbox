from pathlib import Path

import pygame
from robingame.image import load_image, scale_image
from robingame.objects import Game

from slappers_only import conf


class SlappersOnly(Game):
    window_width = conf.WINDOW_HEIGHT
    window_height = conf.WINDOW_WIDTH
    window_caption = "Slappers Only"
    screen_color = (255, 255, 255)
    fps = 60

    def __init__(self):
        super().__init__()

        filename = Path(__file__).parent / "images/loading.png"
        img = scale_image(load_image(filename), scale=5)
        rect = img.get_rect()
        rect.center = self.window.get_rect().center
        self.window.blit(img, rect)
        pygame.display.update()

        from slappers_only.scenes.splash_screen import SplashScreen
        from slappers_only.scenes.manager import Manager

        x, y = self.window.get_rect().center
        self.scenes.add(
            SplashScreen(
                x=x,
                y=y,
                callback=lambda: self.scenes.add(Manager()),
            )
        )


if __name__ == "__main__":
    SlappersOnly().main()
