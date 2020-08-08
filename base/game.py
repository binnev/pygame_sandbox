import pygame

from base.keyhandler import KeyHandler


class Game:
    """This class runs the game"""

    fps = 60
    window_width: int
    window_height: int
    window_caption: str

    def __init__(self):
        pygame.init()
        pygame.font.init()

        window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(self.window_caption)

        self.window = window
        self.clock = pygame.time.Clock()
        KeyHandler.initialise(queue_length=5)
        self.font = pygame.font.Font(pygame.font.match_font("ubuntucondensed"), 30)

    def main(self):
        run = True
        ii = 0
        while run:
            KeyHandler.append(pygame.key.get_pressed())

            if KeyHandler.is_pressed(pygame.K_ESCAPE):
                run = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            print(ii)
            ii += 1
            self.run()
            pygame.display.flip()
            self.clock.tick(self.fps)

    def run(self):
        """Override me"""
        self.window.fill((0, 255, 0))
        text = self.font.render("This is the default game", True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (self.window_width // 2, self.window_height // 2)
        self.window.blit(text, textRect)

    @property
    def screen_size(self):
        return self.window.get_size()

    @property
    def screen_width(self):
        return self.screen_size[0]

    @property
    def screen_height(self):
        return self.screen_size[1]
