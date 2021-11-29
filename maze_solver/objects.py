from pygame import Color
from pygame.surface import Surface

from fighting_game.objects import Entity, Group

SCALING = 10


class NodeTypes:
    EMPTY = " "
    WALL = "W"
    PATH = "."
    EXPLORED = "░"


class Cell(Entity):
    color: tuple

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = col
        self.y = row
        super().__init__()

    def draw(self, surface: Surface, debug: bool = False, color: tuple=None):
        pixel_size = SCALING*0.99
        pixel = Surface((pixel_size, pixel_size))
        color = color or self.color
        pixel.fill(color[:3])
        screen_x = self.x * SCALING
        screen_y = self.y * SCALING
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
        return filter(None, [self.right, self.down, self.left, self.up])

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

    def __init__(self, string):
        self.nodes = Group()
        self.walls = Group()
        self.child_groups = [self.nodes, self.walls]

        rows = [
            [Node(x, y) if cell != NodeTypes.WALL else Wall(x, y) for y, cell in enumerate(row)]
            for x, row in enumerate(string.split("\n"))
        ]
        self.height = len(rows)
        self.width = len(rows[0])

        for x, row in enumerate(rows):
            for y, node in enumerate(row):
                if isinstance(node, Wall):
                    self.add_walls(node)
                    continue  # walls don't have links

                self.add_nodes(node)
                if (x == self.height - 1) and (y == self.width - 1):
                    node.is_finish = True  # this is the end of the maze

                # link with node above
                if x == 0:
                    continue
                node_above = rows[x - 1][y]
                if isinstance(node_above, Node):
                    node.up = node_above
                    node_above.down = node

                # link with node left
                if y == 0:
                    continue
                node_left = rows[x][y - 1]
                if isinstance(node_left, Node):
                    node.left = node_left
                    node_left.right = node

        self.rows = rows

    def add_nodes(self, *nodes):
        self.add_to_group(*nodes, group=self.nodes)

    def add_walls(self, *walls):
        self.add_to_group(*walls, group=self.walls)

    def find_path(self, row=0, col=0):
        return self.depth_first_search(row, col)

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

    def depth_first_search(self, row=0, col=0):
        self.path = list()  # the actual path from start to finish
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

        template = [
            list(map(str, row))
            for row in self.rows
        ]
        for node in path:
            template[node.row][node.col] = NodeTypes.PATH
        return "\n".join("".join(row) for row in template)

    def can_find_path(self, row=0, col=0):
        path = self.find_path(row, col)
        return (0, 0) in path and (self.height - 1, self.width - 1) in path

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        for node in self.path:
            node.draw(surface, color=Color("red"))
        try:
            self.path[-1].draw(surface, color=Color("brown"))
        except IndexError:
            pass


