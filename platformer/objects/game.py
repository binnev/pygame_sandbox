import pygame

from platformer.objects.keyhandlers import KeyHandler


class Game:
    """This class runs the game"""

    def __init__(self, window, fps=60):
        self.window = window
        self.clock = pygame.time.Clock()
        self.key_handler = KeyHandler(queue_length=5)
        self.fps = fps

    @property
    def screen_size(self):
        return self.window.get_size()

    @property
    def screen_width(self):
        return self.screen_size[0]

    @property
    def screen_height(self):
        return self.screen_size[1]

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

            self.window.fill((0, 255, 0))
            pygame.display.flip()
            self.clock.tick(self.fps)
