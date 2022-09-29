import sys

import pygame
from pygame.color import Color
from pygame.surface import Surface

from automata.maze_solver.test_mazes import MAZES
from robingame.input import EventQueue
from robingame.objects import Game


class MazeSolverGame(Game):
    fps = 0
    window_width = 1000
    window_height = 500
    window_caption = "Maze Solver"
    font_name = "ubuntu"
    font_size = 20
    ticks_per_frame = 1  # how many iterations to do between draws
    parental_name = "game"
    screen_color = Color("white")

    def main(self):
        """This is the outermost game function which runs once. It contains the outermost game
        loop. Here's where you should put your main event state machine."""
        from automata.maze_solver.objects import Maze

        for inp, solvable in MAZES:
            inp = "\n".join(inp)
            maze1 = Maze(inp, game=self, x=0, y=0, algorithm="dfs")
            maze2 = Maze(inp, game=self, x=self.window_width // 2, y=0, algorithm="bfs")
            self.add_scene(maze1, maze2)
            super().main()

    def read_inputs(self):
        super().read_inputs()
        for event in EventQueue.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    self.scenes.kill()
                    self.running = False
                if event.key == pygame.K_DOWN:
                    self.ticks_per_frame = max([1, self.ticks_per_frame // 2])
                    print(f"self.ticks_per_frame: {self.ticks_per_frame}")
                if event.key == pygame.K_UP:
                    self.ticks_per_frame *= 2
                    print(f"self.ticks_per_frame: {self.ticks_per_frame}")

    def update(self):
        for _ in range(self.ticks_per_frame):
            super().update()

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        text_bitmap = self.font.render(f"iterations: {self.tick}", True, Color("black"))
        surface.blit(text_bitmap, (0, 0))
