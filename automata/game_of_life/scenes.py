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
