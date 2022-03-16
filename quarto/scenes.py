from typing import TYPE_CHECKING

import pygame
from pygame.sprite import AbstractGroup

from base.input import EventQueue
from base.objects import Entity, Group
from base.stuff.gui_test import mouse_hovering_over
from quarto.objects import QuartoBoard, Piece

if TYPE_CHECKING:
    from quarto.game import QuartoGame


class QuartoMatch(Entity):
    game: "QuartoGame"

    def __init__(self, *groups: AbstractGroup) -> None:
        super().__init__(*groups)

        self.board = QuartoBoard(x=200, y=300)
        self.entities = Group()
        self.selected_pieces = Group()
        self.unused_pieces = Group()
        self.child_groups = [self.entities, self.unused_pieces, self.selected_pieces]
        self.entities.add(
            self.board,
            # NextPiecePillow(),
        )

        self.state = self.state_idle

    def state_idle(self):
        if EventQueue.get(type=pygame.MOUSEBUTTONDOWN, button=pygame.BUTTON_LEFT):
            for piece in self.board.pieces:
                if mouse_hovering_over(piece):
                    self.pick_up(piece)
                    break

        if EventQueue.filter(type=pygame.MOUSEBUTTONUP):
            for piece in self.selected_pieces:
                self.put_down(piece)

        if event := EventQueue.get(type=pygame.MOUSEMOTION):
            dx, dy = event.rel
            for piece in self.selected_pieces:
                piece.rect.centerx += dx
                piece.rect.centery += dy

    def pick_up(self, piece: Piece):
        piece.kill()  # remove from other groups
        self.selected_pieces.add(piece)

    def put_down(self, piece: Piece):
        piece.kill()
        self.board.pieces.add(piece)
