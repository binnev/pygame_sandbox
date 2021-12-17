import sys

import pygame
from pygame.color import Color
from pygame.surface import Surface

from fighting_game.objects import Entity, Group


class AdventOfCodeGame(Entity):
    fps = 60
    window_width = 1000
    window_height = 1000
    window_caption = "Advent of Code"
    font_name = "ubuntu"
    font_size = 20
    parental_name = "game"
    ticks_per_frame = 1  # how many iterations to do between draws

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
        from automata.advent_of_code.menus import MainMenu

        self.add_scene(MainMenu())
        self.debug = False
        self.running = True
        while self.running:
            self.update()
            self.draw(self.window, debug=self.debug)

    def add_scene(self, *objects):
        self.add_to_group(*objects, group=self.scenes)

    def update(self):
        self.events = pygame.event.get()
        if self.debug:
            print(self.tick, self.events)
        for event in self.events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # if event.key == pygame.K_ESCAPE:
                #     pygame.quit()
                #     sys.exit()
                if event.key == pygame.K_F1:
                    self.debug = not self.debug
                if event.key == pygame.K_DOWN:
                    self.fps = max([1, self.fps // 2])
                    print(f"self.fps: {self.fps}")
                if event.key == pygame.K_UP:
                    self.fps *= 2
                    print(f"self.fps: {self.fps}")

        super().update()
        self.clock.tick(self.fps)

        # if there are no scenes to play, exit
        if not self.scenes:
            self.running = False

    def draw(self, surface: Surface, debug: bool = False):
        if self.tick % self.ticks_per_frame == 0:
            surface.fill(Color("black"))  # clear the screen
            super().draw(surface, debug)
            text_bitmap = self.font.render(f"iterations: {self.tick}", True, Color("black"))
            surface.blit(text_bitmap, (0, 0))
            pygame.display.update()  # print to screen
