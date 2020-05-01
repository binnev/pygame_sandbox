# ======= this block has to come first to preserve the pygame loading order ==============
import pygame

from platformer.conf import SCREEN_WIDTH, SCREEN_HEIGHT

pygame.init()
pygame.font.init()
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("")
# ========================================================================================

from platformer.keyhandler import KeyHandler
from platformer.levels import TestLevel, FinalDestination
from platformer.objects import Blob, Ball


class Game:

    def __init__(self):
        self.levels = {
            "test_level": TestLevel,
            "battlefield": FinalDestination,
        }
        self.clock = pygame.time.Clock()
        self.key_handler = KeyHandler(queue_length=5)

    def run_level(self, level_class):
        level = level_class()
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

            window.fill((255, 255, 255))

            # ================== update and draw =========================
            if pressed[pygame.K_a]:
                level.add(Ball(200, 200), type="projectile")
            if pressed[pygame.K_d]:
                debug = not debug
            level.update(keys)
            level.draw(
                window,
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

            window.fill((255, 255, 255))
            pygame.display.flip()
            self.clock.tick(60)


def main():
    game = Game()
    game.main()
    pygame.quit()


if __name__ == "__main__":
    main()
