"""
░▒▓█
"""

from maze_solver.objects import Maze
from maze_solver.test_mazes import MAZES


def path_finder(maze):
    m = Maze(maze)
    return m.can_find_path()


max_size = [0]

for inp, solvable in MAZES:
    inp = "\n".join(inp)
    maze = Maze(inp)

    path = maze.find_path()
    print("-" * 120)
    print(maze.string(path))
    print("\n")
    print("solved" if maze.is_solved else "not solved")
