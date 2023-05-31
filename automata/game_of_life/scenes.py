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
            viewport_center_xy=(1.6, 2.3),
            scale=10,
            groups=(self.boards,),
        )
        self.second_board = InfiniteBoardViewer(
            contents=load_pattern(patterns.BLOCK),
            viewport_center_xy=(2, 2),
            scale=1,
            groups=(self.boards,),
        )

    def draw(self, surface: Surface, debug: bool = False):
        # super().draw(surface, debug)
        main_board_surf = Surface((210, 320))
        main_board_surf.fill(Color("pink"))
        main_rect = main_board_surf.get_rect()
        main_rect.topleft = (10, 10)

        self.main_board.draw(main_board_surf, debug)
        surface.blit(main_board_surf, main_rect)

        second_board_surf = Surface((300, 200))
        second_board_surf.fill(Color("black"))
        second_rect = second_board_surf.get_rect()
        second_rect.topleft = (main_rect.right + 10, main_rect.top)
        self.second_board.draw(second_board_surf, debug)
        surface.blit(second_board_surf, second_rect)

    def zoom_in(self, amount: float):
        for board in self.boards:
            board.scale = max(1, board.scale + amount)
            print(f"scale increased to {board.scale}")

    def zoom_out(self, amount: float):
        for board in self.boards:
            board.scale = max(1, board.scale - amount)
            print(f"scale reduced to {board.scale}")

    def update(self):
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
