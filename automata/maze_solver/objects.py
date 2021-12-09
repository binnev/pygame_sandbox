from pygame import Color
from pygame.surface import Surface

from fighting_game.objects import Entity, Group
from automata.maze_solver.game import MazeSolverGame


class NodeTypes:
    EMPTY = " "
    WALL = "W"
    PATH = "."
    EXPLORED = "░"


class Cell(Entity):
    color: tuple
    maze: "Maze"

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = col
        self.y = row
        super().__init__()

    def draw(self, surface: Surface, debug: bool = False, color: tuple = None):
        pixel_size = self.maze.scaling * 0.99
        pixel = Surface((pixel_size, pixel_size))
        color = color or self.color
        pixel.fill(color[:3])
        screen_x = self.maze.x + (self.x * self.maze.scaling)
        screen_y = self.maze.y + (self.y * self.maze.scaling)
        surface.blit(pixel, (screen_x, screen_y))
        super().draw(surface, debug)


class Node(Cell):
    """Represents an empty (non wall) cell in a maze"""

    row: int
    col: int
    neighbours: list
    up: "Node" = None
    down: "Node" = None
    left: "Node" = None
    right: "Node" = None
    is_finish: bool = False
    explored: bool = False

    @property
    def color(self):
        return Color("orange") if self.explored else Color("gray")

    @property
    def neighbours(self):
        """Prioritize going right and down"""
        return list(filter(None, [self.right, self.down, self.left, self.up]))

    def __repr__(self) -> str:
        return NodeTypes.EXPLORED if self.explored else NodeTypes.EMPTY

    def __str__(self) -> str:
        return self.__repr__()


class Wall(Cell):
    color = Color("black")

    def __str__(self):
        return NodeTypes.WALL


class Maze(Entity):
    is_solved: bool = False
    game: MazeSolverGame
    scaling: int
    x: int
    y: int
    algorithm: str = "dfs"
    parental_name = "maze"

    def __init__(self, string, game, x=0, y=0, algorithm="dfs"):
        self.x = x
        self.y = y
        self.algorithm = algorithm
        self.game = game
        self.nodes = Group()
        self.walls = Group()
        self.child_groups = [self.nodes, self.walls]

        self.rows = self.create_cells(string)
        self.height = len(self.rows)
        self.width = len(self.rows[0])
        self.create_links()

        # the path taken through the maze -- start at the top left
        self.path = list()
        self.path.append(self.rows[0][0])

        self.scaling = min(
            self.game.window_width // 2 // self.width,
            self.game.window_height // self.height,
        )
        super().__init__()

    def create_cells(self, string):
        rows = [
            [
                Node(rr, cc) if cell != NodeTypes.WALL else Wall(rr, cc)
                for cc, cell in enumerate(row)
            ]
            for rr, row in enumerate(string.split("\n"))
        ]
        return rows

    def create_links(self):
        """Link each cell to its neighbours"""
        for rr, row in enumerate(self.rows):
            for cc, cell in enumerate(row):
                if isinstance(cell, Wall):
                    self.add_walls(cell)
                    continue  # walls don't have links

                self.add_nodes(cell)
                if (rr == self.height - 1) and (cc == self.width - 1):
                    cell.is_finish = True  # this is the end of the maze

                # link with node below
                try:
                    node_below = self.rows[rr + 1][cc]
                    if isinstance(node_below, Node):
                        cell.down = node_below
                        node_below.up = cell
                except IndexError:
                    pass

                # link with node to the right
                try:
                    node_right = self.rows[rr][cc + 1]
                    if isinstance(node_right, Node):
                        cell.right = node_right
                        node_right.left = cell
                except IndexError:
                    pass

    def add_nodes(self, *nodes):
        self.add_to_group(*nodes, group=self.nodes)

    def add_walls(self, *walls):
        self.add_to_group(*walls, group=self.walls)

    def find_path(self, row=0, col=0):
        return self.depth_first_search(row, col)

    def breadth_first_search_step(self):
        for node in self.path:
            node.explored = True
        self.path = list({n for node in self.path for n in node.neighbours if not n.explored})
        if any(node.is_finish for node in self.path):
            self.is_solved = True

    def breadth_first_search(self, row=0, col=0):
        """Get the set of open cells that are contiguous with the starting point."""
        path = {(row, col)}
        edge = {*path}
        while True:
            path_size = len(path)
            new_cells = set()
            for cell in edge:
                adjacent = self.adjacent_empty(*cell)
                new_cells = new_cells.union(adjacent)
            edge = new_cells - path
            path = path.union(new_cells)  # add new cells to path
            if len(path) == path_size or ((self.height - 1, self.width - 1) in path):
                break
        return path

    def depth_first_search_step(self):
        if not self.path:  # we backtracked all the way to the beginning. Not solvable.
            return  # not solvable
        node = self.path[-1]
        node.explored = True
        if not node.neighbours:
            return  # not solvable
        # if all neighbours are visited, this is a dead end. Backtrack.
        if all(n.explored for n in node.neighbours):
            self.path.pop()
            return  # continue

        # otherwise, get the first unvisited neighbour
        node = next(n for n in node.neighbours if not n.explored)
        node.explored = True
        self.path.append(node)

        # win condition -- quit early
        if node.is_finish:
            self.is_solved = True

    def depth_first_search(self, row=0, col=0):
        node = self.rows[row][col]
        node.explored = True
        self.path.append(node)

        for _ in range(5000):
            if not self.path:  # we backtracked all the way to the beginning. Not solvable.
                return self.path
            node = self.path[-1]
            if not node.neighbours:
                break
            # if all neighbours are visited, this is a dead end. Backtrack.
            if all(n.explored for n in node.neighbours):
                self.path.pop()
                continue

            # otherwise, get the first unvisited neighbour
            node = next(n for n in node.neighbours if not n.explored)
            node.explored = True
            self.path.append(node)

            # win condition -- quit early
            if node.is_finish:
                self.is_solved = True
                break
        return self.path

    def string(self, path):

        template = [list(map(str, row)) for row in self.rows]
        for node in path:
            template[node.row][node.col] = NodeTypes.PATH
        return "\n".join("".join(row) for row in template)

    def can_find_path(self, row=0, col=0):
        path = self.find_path(row, col)
        return (0, 0) in path and (self.height - 1, self.width - 1) in path

    def update(self):
        if self.is_solved:
            return
        if self.algorithm == "dfs":
            self.depth_first_search_step()
        elif self.algorithm == "bfs":
            self.breadth_first_search_step()
        else:
            raise Exception("I got no algorithm")
        super().update()

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        for node in self.path:
            node.draw(surface, color=Color("red"))
