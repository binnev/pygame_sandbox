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
        # self.child_groups += [
        #     self.boards,
        # ]

        self.main_board = InfiniteBoardViewer(
            contents={
                (3, 0): 1,
                (2, 1): 1,
                (2, 2): 1,
                (1, 3): 1,
                (3, 3): 1,
                (1, 4): 1,
                (0, 5): 1,
            },
            viewport_center=(0, 0),
            scale=1,
            groups=(self.boards,),
        )
        self.second_board = InfiniteBoardViewer(
            contents={
                (3, 0): 1,
                (2, 1): 1,
                (2, 2): 1,
                (1, 3): 1,
                (3, 3): 1,
                (1, 4): 1,
                (0, 5): 1,
            },
            viewport_center=(2, 2),
            scale=1,
            groups=(self.boards,),
        )

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        main_board_surf = Surface((400, 300))
        main_board_surf.fill(Color("black"))
        second_board_surf = Surface((300, 200))
        second_board_surf.fill(Color("black"))

        self.main_board.draw(main_board_surf, debug)
        self.second_board.draw(second_board_surf, debug)

        surface.blit(main_board_surf, (10, 10))
        surface.blit(second_board_surf, (410, 310))

    def zoom_in(self):
        for board in self.boards:
            board.scale = max(1, board.scale + 2)
            print(f"scale increased to {board.scale}")

    def zoom_out(self):
        for board in self.boards:
            board.scale = max(1, board.scale - 2)
            print(f"scale reduced to {board.scale}")

    def update(self):
        super().update()
        # print(f"{pygame.mouse.get_pos()=}")
        if pygame.key.get_pressed()[pygame.K_UP]:
            self.zoom_in()
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            self.zoom_out()
        for event in EventQueue.events:
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.zoom_in()
                else:
                    self.zoom_out()
