import pygame
from pygame import Surface, Color
from pygame.sprite import AbstractGroup
from robingame.input import EventQueue
from robingame.objects import Entity, Group

from automata.game_of_life import patterns
from automata.game_of_life.classes import InfiniteBoard, InfiniteBoardViewer
from automata.game_of_life.patterns import load_pattern


class MainScene(Entity):
    def __init__(self, *groups: AbstractGroup, **kwargs) -> None:
        super().__init__(*groups)

        self.boards = Group()
        self.child_groups += [
            self.boards,
        ]

        self.main_board = InfiniteBoardViewer(
            contents={**load_pattern(patterns.BLOCK)},
            viewport_center_xy=(0, 0),
            rect=(10, 10, 400, 400),
            scale=10,
            groups=(self.boards,),
            **kwargs,
        )
        self.second_board = InfiniteBoardViewer(
            contents=load_pattern(patterns.BLOCK),
            viewport_center_xy=(0, 0),
            rect=(self.main_board.rect.right + 10, self.main_board.rect.top, 400, 400),
            scale=10,
            groups=(self.boards,),
            **kwargs,
        )
        self.second_board.ticks_per_draw = self.second_board.updates_per_draw = 10
        # self.main_board.paused = self.second_board.paused = True

    def update(self):
        """
        [x] zoom: E / Q
        [x] zoom: mousewheel
        [ ] change ticks_per_update: left / right
        [ ] change updates_per_draw: up / down
        [ ] center on centroid: C
        [x] pan: WASD
        [x] pause: Space
        [x] forward 1 (when paused): >
        [ ] back 1 (when paused): <
        [ ] pan: drag w mouse
        [ ] place / remove cell: L / R mouse button
        """
        super().update()
