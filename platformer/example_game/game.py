import pygame

from base.game import Game
from base.keyhandler import KeyHandler
from base.objects.entities import MovingEntity
from platformer.example_game.entities.characters.blob import Blob, Ball
from platformer.example_game.levels import TestLevel, FinalDestination, VolleyballCourt
from platformer.example_game.conf import SCREEN_WIDTH, SCREEN_HEIGHT


class ExampleGame(Game):
    window_height = SCREEN_HEIGHT
    window_width = SCREEN_WIDTH
    window_caption = "pixel smash"

    def __init__(self):
        super().__init__()
        self.levels = {
            "test_level": TestLevel,
            "final_destination": FinalDestination,
            "volleyball_court": VolleyballCourt,
        }

    def run_level(self, level_class):
        level = level_class(game=self)
        # level.add(MovingEntity(50, 200, 50, 50), type="character")
        # level.add(Blob(150, 200, skin=2), type="character")
        level.add(Blob(50, 200), type="character")
        debug = True

        run = True
        while run:
            keys = pygame.key.get_pressed()
            KeyHandler.append(keys)
            pressed = KeyHandler.get_pressed()

            if pressed[pygame.K_ESCAPE]:
                run = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            self.window.fill((255, 255, 255))

            # ================== update and draw =========================
            if pressed[pygame.K_a]:
                level.add(Ball(200, 200), type="projectile")
            if pressed[pygame.K_d]:
                debug = not debug
            level.update()
            level.draw(
                self.window, debug=debug,
            )
            pygame.display.flip()
            self.clock.tick(self.fps)

    def main(self):
        run = True
        while run:
            keys = pygame.key.get_pressed()
            KeyHandler.append(keys)
            pressed = KeyHandler.get_pressed()

            if pressed[pygame.K_ESCAPE]:
                run = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            if pressed[pygame.K_1]:
                self.run_level(self.levels["test_level"])
            if pressed[pygame.K_2]:
                self.run_level(self.levels["final_destination"])
            if pressed[pygame.K_3]:
                self.run_level(self.levels["volleyball_court"])

            self.window.fill((255, 255, 255))
            pygame.display.flip()
            self.clock.tick(self.fps)
