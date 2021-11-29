"""
░▒▓█
"""
import sys

import pygame

from maze_solver.objects import Maze
from maze_solver.test_mazes import MAZES


def path_finder(maze):
    m = Maze(maze)
    return m.can_find_path()


max_size = [0]

fps = 10
window_width = 1000
window_height = 1000
window_caption = "Langton's Ant Simulator"
font_name = "ubuntu"
font_size = 20
ticks_per_frame = 1  # how many iterations to do between draws

pygame.init()
pygame.font.init()
font = pygame.font.Font(pygame.font.match_font(font_name), font_size)
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption(window_caption)
clock = pygame.time.Clock()

for inp, solvable in MAZES:
    inp = "\n".join(inp)
    maze = Maze(inp)
    running = True
    debug = False
    tick = 0
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_F1:
                    debug = not debug
                if event.key == pygame.K_SPACE:
                    running = False
                if event.key == pygame.K_DOWN:
                    fps = max([1, fps // 2])
                    print(f"fps: {fps}")
                if event.key == pygame.K_UP:
                    fps *= 2
                    print(f"fps: {fps}")

        maze.update()

        window.fill(pygame.Color("white"))  # clear the screen
        maze.draw(window)
        pygame.display.update()  # print to screen

        tick += 1
        clock.tick(fps)


