import sys

import pygame
from pygame import Surface

from base.inputs.gamecube import GamecubeController
from fighting_game import sounds
from fighting_game.conf import *
from fighting_game.inputs import Keyboard0, Keyboard1
from fighting_game.objects import Entity, Group


class FightingGame(Entity):
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
        pygame.init()

        self.scenes = Group()
        self.child_groups = [self.scenes]

        pygame.font.init()
        self.font = pygame.font.Font(pygame.font.match_font(self.font_name), self.font_size)
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(self.window_caption)
        self.clock = pygame.time.Clock()

        # input devices
        # todo; should input devices be entities too?! All they need is an .update() method and a
        #  self.draw() that does nothing...
        self.keyboard0 = Keyboard0()
        self.keyboard1 = Keyboard1()
        self.controller0 = GamecubeController(controller_id=0)
        self.controller1 = GamecubeController(controller_id=1)
        self.input_devices = [
            self.keyboard0,
            self.keyboard1,
            self.controller0,
            self.controller1,
        ]

    def main(self):
        """This is the outermost game function which runs once. It contains the outermost game
        loop. Here's where you should put your main event state machine."""
        from fighting_game.scenes import SandBox

        self.add_scene(SandBox())
        self.debug = False
        self.running = True
        while self.running:
            self.update()
            self.draw(self.window, debug=self.debug)

    def add_scene(self, *objects):
        self.add_to_group(*objects, group=self.scenes)

    def update(self):
        # read inputs first
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
                if event.key == pygame.K_s:
                    sounds.announcement.play()

        # todo: this should just be self.inputs.update which super().update() will take care of.
        #   (make sure that inputs is the first group so that inputs are read at the start of tick)
        for device in self.input_devices:
            device.read_new_inputs()

        super().update()
        self.clock.tick(self.fps)

        # if there are no scenes to play, exit
        if not self.scenes:
            self.running = False

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        pygame.display.update()  # print to screen
