import sys

import pygame
from pygame.color import Color
from pygame.surface import Surface

from fighting_game.objects import Entity, Group
from maze_solver.test_mazes import MAZES


class MazeSolverGame(Entity):
    fps = 60
    window_width = 1000
    window_height = 1000
    window_caption = "Maze Solver"
    font_name = "ubuntu"
    font_size = 20
    ticks_per_frame = 10  # how many iterations to do between draws
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

    def main(self):
        """This is the outermost game function which runs once. It contains the outermost game
        loop. Here's where you should put your main event state machine."""
        from maze_solver.objects import Maze

        for inp, solvable in MAZES:
            inp = "\n".join(inp)
            self.maze = Maze(inp, game=self)
            self.running = True
            self.debug = False

            self.add_scene(self.maze)
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
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_F1:
                    self.debug = not self.debug
                if event.key == pygame.K_SPACE:
                    self.maze.kill()
                    self.running = False
                if event.key == pygame.K_DOWN:
                    self.ticks_per_frame = max([1, self.ticks_per_frame // 2])
                    print(f"self.ticks_per_frame: {self.ticks_per_frame}")
                if event.key == pygame.K_UP:
                    self.ticks_per_frame *= 2
                    print(f"self.ticks_per_frame: {self.ticks_per_frame}")

        super().update()
        # self.clock.tick(self.fps)

        # if there are no scenes to play, exit
        if not self.scenes:
            self.running = False

    def draw(self, surface: Surface, debug: bool = False):
        if self.tick % self.ticks_per_frame == 0:
            surface.fill(Color("white"))  # clear the screen
            super().draw(surface, debug)
            text_bitmap = self.font.render(f"iterations: {self.tick}", True, Color("black"))
            surface.blit(text_bitmap, (0, 0))
            pygame.display.update()  # print to screen
