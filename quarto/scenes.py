import math
from random import randint
from typing import TYPE_CHECKING

import pygame
from pygame.sprite import AbstractGroup, spritecollide

from base.input import EventQueue
from base.objects import Entity, Group
from base.utils import mouse_hovering_over
from quarto.objects import QuartoBoard, Piece, UnusedPiecePad, Square
from quarto.utils import distance

if TYPE_CHECKING:
    from quarto.game import QuartoGame


class QuartoMatch(Entity):
    game: "QuartoGame"

    def __init__(self, *groups: AbstractGroup) -> None:
        super().__init__(*groups)

        self.board = QuartoBoard(x=100, y=300)
        self.unused_piece_pad = UnusedPiecePad(x=800, y=300)
        self.entities = Group()
        self.selected_pieces = Group()
        self.unused_pieces = Group()
        self.child_groups = [self.entities, self.unused_pieces, self.selected_pieces]
        self.entities.add(
            self.board,
            self.unused_piece_pad,
            # NextPiecePillow(),
        )

        self.state = self.state_idle
        ii = 0
        for tall in True, False:
            for hollow in True, False:
                for square in True, False:
                    for black in True, False:
                        radius = 130
                        angle_deg = -90 - 20 * ii
                        angle_rad = angle_deg / 180 * math.pi
                        screen_x = self.unused_piece_pad.x + radius * math.cos(angle_rad)
                        screen_y = self.unused_piece_pad.y + radius * math.sin(angle_rad) // 2
                        piece = Piece(
                            screen_x, screen_y, tall=tall, hollow=hollow, square=square, black=black
                        )
                        self.unused_pieces.add(piece)
                        ii += 1

    def state_idle(self):
        if EventQueue.get(type=pygame.MOUSEBUTTONDOWN, button=pygame.BUTTON_LEFT):
            for piece in [*self.unused_pieces_backward(), *self.board.pieces_backward()]:
                if mouse_hovering_over(piece):
                    self.pick_up(piece)
                    break

        if EventQueue.filter(type=pygame.MOUSEBUTTONUP):
            for piece in self.selected_pieces:
                self.put_down(piece)

    def unused_pieces_backward(self):
        for piece in self.unused_pieces.sprites()[::-1]:
            yield piece

    def pick_up(self, piece: Piece):
        piece.kill()  # remove from other groups
        if piece.board_square:
            piece.board_square.remove_piece(piece)
        self.selected_pieces.add(piece)
        mx, my = pygame.mouse.get_pos()
        dx = piece.x - mx
        dy = piece.y - my
        piece.mouse_offset = (dx, dy)
        piece.state = piece.state_grabbed

    def put_down(self, piece: Piece):
        piece.kill()
        piece.state = piece.state_main
        if colliding_squares := spritecollide(piece, self.board.squares, dokill=False):
            nearest_square = min(
                colliding_squares, key=lambda s: distance(s.rect.midbottom, piece.rect.midbottom)
            )
            if not nearest_square.piece:
                nearest_square.add_piece(piece)
                self.board.pieces.add(piece)
                return
        self.unused_pieces.add(piece)
