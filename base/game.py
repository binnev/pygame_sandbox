import pygame

from base.inputs.keyboard import KeyboardInputQueue


class Game:
    """This class runs the game"""

    fps = 60
    window_width: int
    window_height: int
    window_caption: str
    ticks_per_frame: int
    font_name: str = "ubuntucondensed"
    font_size: int = 30

    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.font = pygame.font.Font(pygame.font.match_font(self.font_name), self.font_size)
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(self.window_caption)
        self.clock = pygame.time.Clock()

        # input devices
        self.keyboard = KeyboardInputQueue()
        self.input_devices = [self.keyboard]

    def main(self):
        """This is the outermost game function which runs once. It contains the outermost game
        loop. Here's where you should put your main event state machine."""
        self.tick = 0
        run = True
        while run:
            # input devices should be read once per tick in the main game loop.
            # That can be the single source of truth regarding inputs.
            for device in self.input_devices:
                device.read_new_inputs()

            # provide a default exit option
            if self.keyboard.is_pressed(pygame.K_ESCAPE):
                run = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            self.window.fill((0, 255, 0))
            text = self.font.render("This is the default game", True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (self.window_width // 2, self.window_height // 2)
            self.window.blit(text, textRect)

            pygame.display.flip()
            self.clock.tick(self.fps)
            self.tick += 1

    @property
    def screen_size(self):
        return self.window.get_size()

    @property
    def screen_width(self):
        return self.screen_size[0]

    @property
    def screen_height(self):
        return self.screen_size[1]
