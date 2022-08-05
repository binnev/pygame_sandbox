import sys

import pygame
from pygame.color import Color
from pygame.surface import Surface

from base.input import EventQueue
from base.objects.entity import Entity, Group
from base.objects.helpers import FpsTracker


class Game(Entity):
    """Special case of Entity; it is at the very top of the object tree."""

    fps: int = 60
    window_width: int = 500
    window_height: int = 500
    window_caption: str = ""
    font_name: str = "ubuntucondensed"
    font_size: int = 30
    parental_name = "game"
    screen_color = Color("black")
    debug = False

    def __init__(self):
        super().__init__()
        pygame.init()

        self.scenes = Group()
        self.scenes.add()
        self.debug_helpers = Group()
        self.debug_helpers.add(FpsTracker())
        self.child_groups = [self.scenes, self.debug_helpers]

        pygame.font.init()
        self.font = pygame.font.Font(pygame.font.match_font(self.font_name), self.font_size)
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(self.window_caption)
        self.clock = pygame.time.Clock()

    def main(self):
        """This is the outermost game function which runs once. It contains the outermost game
        loop. Here's where you should put your main event state machine."""
        self.running = True
        while self.running:
            self._update()
            self._draw(self.window, debug=self.debug)
        pygame.quit()
        sys.exit()

    def add_scene(self, *objects):
        self.add_to_group(*objects, group=self.scenes)

    def read_inputs(self):
        """I've put this in a separate method because I don't like the idea of putting the inputs
        in the same list as other child groups. The order might get ruined, or a subclass might
        overwrite the list. It's crucial that the inputs are read before updating."""
        EventQueue.update()
        for event in EventQueue.events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                self.debug = not self.debug

    def print_debug_info(self):
        pass

    def _update(self):
        """
        1. read inputs
        2. update
        """
        self.read_inputs()
        if self.debug:
            self.print_debug_info()
        self.update()
        if self.fps:
            self.clock.tick(self.fps)

    def _draw(self, surface: Surface, debug: bool = False):
        surface.fill(self.screen_color)  # clear the screen
        self.draw(surface, debug)
        pygame.display.update()  # print to screen
