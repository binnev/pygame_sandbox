import sys

from fighting_game.scenes import *
from fighting_game.conf import *

class FightingGame(Scene):
    fps = FPS
    window_width = SCREEN_WIDTH
    window_height = SCREEN_HEIGHT
    window_caption = "FIGHTING GAME"
    frame_duration = 3
    font_name = "ubuntu"
    font_size = 50
    parental_name = "game"

    def __init__(self):
        super().__init__()

        self.scenes = Group()
        self.groups = [self.scenes]

        pygame.font.init()
        self.font = pygame.font.Font(pygame.font.match_font(self.font_name), self.font_size)
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(self.window_caption)
        self.clock = pygame.time.Clock()

        # input devices
        # todo; should input devices be entities too?! All they need is an .update() method and a
        #  self.draw() that does nothing...
        self.keyboard = KeyboardInput()
        self.input_devices = [self.keyboard]

    def main(self):
        """This is the outermost game function which runs once. It contains the outermost game
        loop. Here's where you should put your main event state machine."""
        self.add_scene(SandBox())
        self.debug = True
        self.tick = 0
        self.running = True
        while self.running:
            self.update()
            self.draw(self.window, debug=self.debug)

    def add_scene(self, *objects):
        self.add_to_group(*objects, group=self.scenes)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_F1:
                    self.debug = not self.debug

        for device in self.input_devices:
            device.read_new_inputs()

        for group in self.groups:
            group.update()
        self.clock.tick(self.fps)
        self.tick += 1

        # if there are no scenes to play, exit
        if not self.scenes:
            self.running = False

    def draw(self, surface, debug=False):
        super().draw(surface, debug)
        pygame.display.update()  # print to screen
