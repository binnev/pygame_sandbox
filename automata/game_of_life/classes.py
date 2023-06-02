import json
import logging
import math
import time
from collections import deque

import matplotlib
import numpy
import pygame.mouse
from pygame import Surface, Color, Rect
from robingame.image import scale_image
from robingame.input import EventQueue
from robingame.objects import Entity, Group
from robingame.text.font import fonts
from robingame.utils import SparseMatrix, Coord

from automata.game_of_life import threshold

logger = logging.getLogger(__file__)


class InfiniteBoard(Entity):
    """
    This class is solely responsible for calculating the next state in a Game of Life simulation.
    It uses a SparseMatrix to represent only the live cells in order to save memory + computation.
    It is not aware of any meta game stuff like FPS.
    """

    contents: SparseMatrix[Coord:int]

    def __init__(
        self,
        contents=None,
        overpopulation_threshold=threshold.OVERPOPULATION,
        underpopulation_threshold=threshold.UNDERPOPULATION,
        reproduction_threshold=threshold.REPRODUCTION,
        groups: tuple[Group] = (),
    ) -> None:
        super().__init__(*groups)
        self.contents = SparseMatrix(contents or {})
        self.overpopulation_threshold = overpopulation_threshold
        self.underpopulation_threshold = underpopulation_threshold
        self.reproduction_threshold = reproduction_threshold

    def iterate(self):
        """
        Can't use .update() for this because that also increments self.tick, and we want to be
        able to do multiple updates per tick.
        """
        # Sparse matrix to store the coordinates of any cell (live or dead) that has live
        # neighbours, in the form: {coord: number_of_live_neighbours}.
        live_neighbours_matrix = SparseMatrix[Coord:int]()

        # Iterate once over all the currently live cells, and grab the coordinates of their
        # neighbours. For each of these neighbours, add +1 to their live neighbour count.
        # O(n_cells)
        for cell in self.contents:
            for neighbour in self.neighbours(cell):
                count = live_neighbours_matrix.get(neighbour, 0)
                live_neighbours_matrix[neighbour] = count + 1

        # sparse matrix to contain the live cells for the next iteration
        new = SparseMatrix()

        # Iterate once over the live_neighbours_matrix, and use each cell's number of live
        # neighbours to decide if it is alive in the next iteration.
        for cell, live_neighbours in live_neighbours_matrix.items():
            alive = cell in self.contents
            if alive:
                # 2. Any live cell with two or three live neighbours lives on to the next generation.
                if (
                    self.underpopulation_threshold
                    <= live_neighbours
                    <= self.overpopulation_threshold
                ):
                    age = self.contents[cell]
                    new[cell] = age + 1
            else:
                # 4. Any dead cell with exactly three live neighbours becomes a live cell, as if by
                # reproduction.
                if live_neighbours == self.reproduction_threshold:
                    new[cell] = 1

        self.contents = new

    def neighbours(self, coord: Coord) -> tuple[Coord, ...]:
        """
        Get the coordinates of all neighbouring cells, including diagonals.
        """
        x, y = coord
        return (
            (x - 1, y - 1),
            (x - 1, y),
            (x - 1, y + 1),
            (x, y - 1),
            (x, y + 1),
            (x + 1, y - 1),
            (x + 1, y),
            (x + 1, y + 1),
        )


class InfiniteBoardViewer(InfiniteBoard):
    """
    Subclass to draw an InfiniteBoard board onto a surface.
    Scaling is absolute:
        1x scale means each cell is 1x1 px.
        10x scale means each cell is 10x10 px.
    where 'px' means screen pixels

    TODO:
        [x] zoom: E / Q
        [x] zoom: mousewheel
        [x] change ticks_per_update: left / right
        [x] change iterations_per_update: up / down
        [x] center on centroid: C
        [x] pan: WASD
        [x] pause: Space
        [x] forward 1 (when paused): >
        [x] back 1 (when paused): <
        [ ] pan: drag w mouse
        [ ] place / remove cell: L / R mouse button
        [x] save / load to file
    """

    viewport_center_xy: tuple[float, float]  # coordinate on which to center the viewport
    scale: float
    num_colors: int
    colormap = matplotlib.cm.viridis_r
    background_color = (30,) * 3
    rect: Rect  # position and size of self in screen coordinates
    paused: bool = False
    ticks_per_update: int = 1  # More = slower FPS and game speed
    iterations_per_update: int = 1  # More = faster game speed, same FPS

    def __init__(
        self,
        *args,
        viewport_center_xy: tuple[float, float] = (0.0, 0.0),
        scale: float = 4,
        num_colors: int = 100,
        rect: Rect | tuple,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.scale = scale
        self.num_colors = num_colors
        self.viewport_center_xy = viewport_center_xy
        self.calculate_colors()
        self.rect = Rect(*rect)
        self.image = Surface(self.rect.size)
        self.history: deque[SparseMatrix] = deque(maxlen=50)

    def zoom(self, amount: float):
        self.scale = max(0.1, self.scale + amount)

    def pan(self, x: float = 0, y: float = 0):
        self.viewport_center_xy = (
            self.viewport_center_xy[0] + x,
            self.viewport_center_xy[1] + y,
        )

    def iterate(self):
        self.history.append(self.contents)
        super().iterate()

    def update(self):
        super().update()

        if not self.paused and self.tick % self.ticks_per_update == 0:
            for _ in range(self.iterations_per_update):
                self.iterate()
        mouse_pos = pygame.mouse.get_pos()
        is_focused = self.rect.contains((*mouse_pos, 0, 0))

        if is_focused:
            PAN_SPEED = 10 / self.scale
            keys_down = pygame.key.get_pressed()
            if keys_down[pygame.K_e]:
                self.zoom(0.2)
            if keys_down[pygame.K_q]:
                self.zoom(-0.2)
            if keys_down[pygame.K_w]:
                self.pan(y=-PAN_SPEED)
            if keys_down[pygame.K_s]:
                self.pan(y=PAN_SPEED)
            if keys_down[pygame.K_a]:
                self.pan(x=-PAN_SPEED)
            if keys_down[pygame.K_d]:
                self.pan(x=PAN_SPEED)
            if keys_down[pygame.K_c]:
                if keys_down[pygame.K_LSHIFT]:
                    self.center_on_oldest()
                elif keys_down[pygame.K_LCTRL]:
                    self.center_on_middle()
                else:
                    self.center_on_centroid()

            for event in EventQueue.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    if self.paused:
                        if event.key == pygame.K_PERIOD:
                            self.iterate()
                        if event.key == pygame.K_COMMA:
                            self.back_one()
                        if event.key == pygame.K_k:
                            self.save()
                        if event.key == pygame.K_l:
                            self.load()
                    if event.key == pygame.K_DOWN:
                        self.ticks_per_update *= 2
                    if event.key == pygame.K_UP:
                        self.ticks_per_update = max(1, self.ticks_per_update // 2)
                    if event.key == pygame.K_RIGHT:
                        self.iterations_per_update *= 2
                    if event.key == pygame.K_LEFT:
                        self.iterations_per_update = max(1, self.iterations_per_update // 2)

                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        self.zoom(2)
                    else:
                        self.zoom(-2)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.paused:
                        if event.button == 1:
                            uv = event.pos
                            xy = self.screen_uv_to_board_xy(uv)
                            print(f"Mouse click at {uv=}, {xy=}")
                            xy = tuple(map(int, xy))
                            self.handle_click(xy)

    def handle_click(self, xy: Coord):
        """
        If cell is alive, kill it. If cell is dead, make it alive.
        """
        if xy in self.contents:
            self.contents.pop(xy)
            print(f"Killed cell at {xy}")
        else:
            self.contents[xy] = 1
            print(f"Created cell at {xy}")

    def viewport_rect(self) -> Rect:
        image_width, image_height = self.image.get_rect().size
        viewport_width = math.ceil(image_width / self.scale)
        viewport_height = math.ceil(image_height / self.scale)
        viewport = Rect(0, 0, viewport_width, viewport_height)
        viewport = viewport.inflate(2, 2)  # make 1 px bigger on all sides for safety
        viewport.center = self.viewport_center_xy
        return viewport

    def draw(self, surface: Surface, debug: bool = False):
        """
        xy = sparse matrix coordinates
        ij = small bitmap pixel indices
        ab = large bitmap pixel indices
        uv = screen coordinates
        viewport = Rect in xy-space to select visible cells. Roughly equal to screen_size/scale
        small_img = Surface with same dimensions as viewport (pixels are used to display cells)
        large_img = small_img scaled up to full size
        """
        super().draw(surface, debug)
        t1 = time.perf_counter()

        # 0. clear old image
        self.image.fill(self.background_color)

        # 1. Choose viewport in xy coordinates to filter for visible cells
        # 2. Round out to nearest int, record x/y min/max range.
        viewport_center_x, viewport_center_y = self.viewport_center_xy
        viewport = self.viewport_rect()

        # 3. Record offset from absolute xy coords to small_img coords (ij)
        i0, j0 = viewport.topleft

        # 4. Create small bitmap on which to draw pixels
        small_img = Surface(viewport.size)
        small_img.fill(self.background_color)

        # 5. Filter visible cells
        to_draw = {
            coord: age
            for coord, age in self.contents.items()
            if viewport.contains((*coord, 1, 1))  # 1x1 pixel at coord location
        }

        # 6. Draw visible cells on small bitmap
        for (x, y), age in to_draw.items():
            color = self.get_color(age)
            ij = (x - i0, y - j0)  # matrix coords to pixel indices
            small_img.set_at(ij, color)

        # 7. Scale small bitmap up to full size
        big_img = scale_image(small_img, self.scale)

        # 8. Calculate viewport center position in large bitmap coords
        # small_img pixel index to large_img coords
        # a = scale * i + (scale - 1) / 2
        # b = scale * j + (scale - 1) / 2
        viewport_center_i: float = viewport_center_x - i0
        viewport_center_j: float = viewport_center_y - j0
        viewport_center_a: float = (self.scale * viewport_center_i) + (self.scale - 1) / 2
        viewport_center_b: float = (self.scale * viewport_center_j) + (self.scale - 1) / 2

        # 9. Calculate the uv offset required to position viewport_center_ab on the screen center
        center_u, center_v = self.image.get_rect().center
        delta_u = center_u - viewport_center_a
        delta_v = center_v - viewport_center_b
        self.image.blit(big_img, (delta_u, delta_v))

        if debug:
            text = "\n".join(
                [
                    f"tick: {self.tick}",
                    f"scale: {self.scale:0.2f}",
                    f"ticks_per_update: {self.ticks_per_update}",
                    f"iterations_per_update: {self.iterations_per_update}",
                ]
            )
            fonts.cellphone_white.render(self.image, text, scale=1.5)

        surface.blit(self.image, self.rect)
        t2 = time.perf_counter()
        logger.info(f"Population {len(self.contents)}, drew {len(to_draw)} in {t2-t1:.5f} sec")

    def calculate_colors(self):
        """Sample a colormap based on the longest ruleset of child ants"""
        samples = numpy.linspace(0, 1, self.num_colors)
        colors = [tuple(map(int, color[:3])) for color in self.colormap(samples) * 256]
        self.colors = colors

    def get_color(self, age: int):
        try:
            return self.colors[age]
        except IndexError:
            return self.colors[-1]

    def center_on_centroid(self):
        """
        Center the viewport on the center of mass of the cells.
        Assuming that each cell has a mass of 1.
        """
        total_mass = len(self.contents)  # each cell has a mass of 1
        x_center = sum(x for x, y in self.contents) / total_mass
        y_center = sum(y for x, y in self.contents) / total_mass
        self.viewport_center_xy = (x_center, y_center)

    def center_on_oldest(self):
        """
        Center the viewport on the center of mass of the cells.
        Use the cells' age as their mass in this calculation. This should move the viewport
        closer to older cells.
        """
        total_mass = sum(self.contents.values())  # use cell age as weight
        x_center = sum(x * age for (x, y), age in self.contents.items()) / total_mass
        y_center = sum(x * age for (x, y), age in self.contents.items()) / total_mass
        self.viewport_center_xy = (x_center, y_center)

    def center_on_middle(self):
        """
        Center the viewport on the middle of the group of cells.
        """
        xmin, xmax = self.contents.xlim
        ymin, ymax = self.contents.ylim
        x_center = xmin + (xmax - xmin) / 2
        y_center = ymin + (ymax - ymin) / 2
        self.viewport_center_xy = (x_center, y_center)

    def back_one(self):
        if self.history:
            self.contents = self.history.pop()

    def save(self, filename: str = "game_of_life.json"):
        data = dict(
            overpopulation_threshold=self.overpopulation_threshold,
            underpopulation_threshold=self.underpopulation_threshold,
            reproduction_threshold=self.reproduction_threshold,
            paused=self.paused,
            contents=to_json(self.contents),
            history=list(map(to_json, self.history)),
        )
        with open(filename, "w") as file:
            json.dump(data, file)

    def load(self, filename: str = "game_of_life.json"):
        with open(filename, "r") as file:
            data = json.load(file)
        self.contents = from_json(data["contents"])
        self.overpopulation_threshold = data["overpopulation_threshold"]
        self.underpopulation_threshold = data["underpopulation_threshold"]
        self.reproduction_threshold = data["reproduction_threshold"]
        self.paused = data["paused"]
        self.history.clear()
        self.history.extend(map(from_json, data["history"]))

    def screen_uv_to_board_xy(self, uv: Coord) -> Coord:
        """
        Convert screen coordinates (u, v) to board coordinates (x, y)
        """
        u, v = uv
        viewport = self.viewport_rect()
        self_origin_u, self_origin_v = self.rect.topleft
        x = viewport.x + (u - self_origin_u) / self.scale
        y = viewport.y + (v - self_origin_v) / self.scale
        return (x, y)


def to_json(matrix: SparseMatrix) -> dict[str:int]:
    """
    JSON doesn't allow using tuples as object keys, so we need to convert to string
    """
    return {f"{x},{y}": value for (x, y), value in matrix.items()}


def from_json(json_: dict[str:int]) -> SparseMatrix:
    matrix = SparseMatrix()
    for xy_string, value in json_.items():
        x, y = xy_string.split(",")
        x = int(x)
        y = int(y)
        matrix[(x, y)] = value
    return matrix
