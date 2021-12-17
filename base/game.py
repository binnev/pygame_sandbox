import sys

import pygame
from pygame.color import Color
from pygame.surface import Surface

from base.event import EventQueue
from base.inputs.keyboard import KeyboardInputQueue
from fighting_game.objects import Group


class Game(Entity):
    """Special case of Entity; it is at the very top of the object tree."""

    fps = 60
    window_width: int
    window_height: int
    window_caption: str
    font_name: str = "ubuntucondensed"
    font_size: int = 30
    parental_name = "game"
    screen_color = Color("black")

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

    def main(self):
        """This is the outermost game function which runs once. It contains the outermost game
        loop. Here's where you should put your main event state machine."""
        self.debug = False
        self.running = True
        if not self.scenes:
            raise Exception("You need to add an initial scene")
        while self.running:
            self.update()
            self.draw(self.window, debug=self.debug)

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

        for device in self.input_devices:
            device.read_new_inputs()

    def print_debug_info(self):
        print(self.tick, EventQueue.events)

    def update(self):
        """
        1. read inputs
        2. update
        """
        self.read_inputs()
        if self.debug:
            self.print_debug_info()
        super().update()
        self.clock.tick(self.fps)

        # if there are no scenes to play, exit
        if not self.scenes:
            self.running = False

    def draw(self, surface: Surface, debug: bool = False):
        surface.fill(self.screen_color)  # clear the screen
        super().draw(surface, debug)
        pygame.display.update()  # print to screen
