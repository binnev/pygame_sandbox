import sys

import pygame

from fighting_game.inputs import KeyboardInput


# todo: subclass Scene here?
class FightingGame:
    fps = 60
    window_width = 1600
    window_height = 900
    window_caption = "FIGHTING GAME"
    frame_duration = 3
    font_name = "ubuntu"
    font_size = 50

    def __init__(self):
        pygame.font.init()

        self.font = pygame.font.Font(pygame.font.match_font(self.font_name), self.font_size)
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(self.window_caption)
        self.clock = pygame.time.Clock()

        # input devices
        self.keyboard = KeyboardInput()
        self.input_devices = [self.keyboard]

        self.scenes = Group()

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

        self.scenes.update()
        self.clock.tick(self.fps)
        self.tick += 1

        # if there are no scenes to play, exit
        if not self.scenes:
            self.running = False

    def draw(self, surface, debug=False):
        self.window.fill((255, 255, 255))
        self.scenes.draw(surface, debug)
        pygame.display.update()

    def add_scene(self, scene):
        scene.game = self
        self.scenes.add(scene)

    def main(self):
        """This is the outermost game function which runs once. It contains the outermost game
        loop. Here's where you should put your main event state machine."""
        self.add_scene(SandBox(game=self))
        self.debug = True
        self.tick = 0
        self.running = True
        while self.running:

            self.update()
            self.draw(self.window, debug=self.debug)





from fighting_game.conf import SCREEN_WIDTH, SCREEN_HEIGHT
from fighting_game.objects import Platform



