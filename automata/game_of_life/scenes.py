import pygame
from pygame import Surface, Color
from pygame.sprite import AbstractGroup
from robingame.input import EventQueue
from robingame.objects import Entity, Group

from automata.game_of_life import patterns
from automata.game_of_life.classes import InfiniteBoard, InfiniteBoardViewer
from automata.game_of_life.patterns import load_pattern


class MainScene(Entity):
    def __init__(self, *groups: AbstractGroup) -> None:
        super().__init__(*groups)

        self.boards = Group()
        self.child_groups += [
            self.boards,
        ]

        self.main_board = InfiniteBoardViewer(
            contents={**load_pattern(patterns.BLOCK)},
            viewport_center_xy=(0, 0),
            rect=(10, 10, 210, 320),
            groups=(self.boards,),
        )
        self.second_board = InfiniteBoardViewer(
            contents=load_pattern(patterns.BLOCK),
            viewport_center_xy=(0, 0),
            rect=(self.main_board.rect.right + 10, self.main_board.rect.top, 300, 200),
            groups=(self.boards,),
        )

    def zoom_in(self, amount: float):
        for board in self.boards:
            board.scale = max(1, board.scale + amount)
            print(f"scale increased to {board.scale}")

    def zoom_out(self, amount: float):
        for board in self.boards:
            board.scale = max(1, board.scale - amount)
            print(f"scale reduced to {board.scale}")

    def update(self):
        """
        zoom: + / -
        change ticks_per_update: left / right
        change updates_per_draw: up / down
        center on centroid: C
        pan: WASD / drag w mouse
        pause: Space
        forward 1 (when paused): >
        back 1 (when paused): <
        place / remove cell: L / R mouse button
        """
        super().update()
        if pygame.key.get_pressed()[pygame.K_UP]:
            self.zoom_in(0.2)
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            self.zoom_out(0.2)
        for event in EventQueue.events:
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.zoom_in(2)
                else:
                    self.zoom_out(2)
