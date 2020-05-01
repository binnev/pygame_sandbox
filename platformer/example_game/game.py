import pygame

from platformer.example_game.entities.characters.blob import Blob, Ball
from platformer.example_game.levels import TestLevel, FinalDestination
from platformer.objects.game import Game


class ExampleGame(Game):

    def __init__(self, window):
        super().__init__(window)
        self.levels = {
            "test_level": TestLevel,
            "battlefield": FinalDestination,
        }

    def run_level(self, level_class):
        level = level_class(self)
        character = Blob(50, 200)
        level.add(character, type="character")
        debug = False

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
            self.clock.tick(60)

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
                self.run_level(self.levels["battlefield"])

            self.window.fill((255, 255, 255))
            pygame.display.flip()
            self.clock.tick(60)
