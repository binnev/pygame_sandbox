import pygame

from platformer.example_game.entities.characters.blob import Blob, Ball
from platformer.example_game.levels import TestLevel, FinalDestination
from platformer.objects.entities import MovingEntity
from platformer.objects.game import Game


class ExampleGame(Game):

    def __init__(self, window, fps=None):
        super().__init__(window, fps)
        self.levels = {
            "test_level": TestLevel,
            "final_destination": FinalDestination,
        }

    def run_level(self, level_class):
        level = level_class(self)
        level.add(MovingEntity(50, 200, 50, 50), type="character")
        # level.add(Blob(50, 200), type="character")
        # level.add(Blob(150, 200, skin=2), type="character")
        debug = True

        run = True
        while run:
            keys = pygame.key.get_pressed()
            self.key_handler.update(keys)
            pressed = self.key_handler.get_pressed()

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
            level.update(keys)
            level.draw(
                self.window,
                debug=debug,
            )
            pygame.display.flip()
            self.clock.tick(self.fps)

    def main(self):
        run = True
        while run:
            keys = pygame.key.get_pressed()
            self.key_handler.update(keys)
            pressed = self.key_handler.get_pressed()

            if pressed[pygame.K_ESCAPE]:
                run = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            if pressed[pygame.K_1]:
                self.run_level(self.levels["test_level"])
            if pressed[pygame.K_2]:
                self.run_level(self.levels["final_destination"])

            self.window.fill((255, 255, 255))
            pygame.display.flip()
            self.clock.tick(self.fps)
