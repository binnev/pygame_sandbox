from typing import TYPE_CHECKING

import pygame
from pygame import Surface, Color
from pygame.rect import Rect

from base.animation import recolor_image
from base.input import EventQueue
from base.objects import PhysicalEntity, Group
from base.stuff.gui_test import mouse_hovering_over
from chess import conf
from chess.assets.pieces import chess_pieces
from chess.constants import WHITE, BLACK
from chess.gui.utils import distance
from fighting_game.particles import random_float, Particle, random_int


if TYPE_CHECKING:
    from chess.gui.classes.board import GuiBoard


class GuiPiece(PhysicalEntity):
    width = conf.SQUARE_SIZE
    height = conf.SQUARE_SIZE
    sprite_name: str
    board: "GuiBoard"

    def __init__(self, x, y, team=WHITE, *groups):
        super().__init__(*groups)
        self.team = team
        self.rect = Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.image = chess_pieces[self.sprite_name].play(0)
        if self.team != WHITE:
            self.image = recolor_image(self.image, {(255, 255, 255): Color("black")})
        self.state = self.state_idle
        self.particles = Group()
        self.child_groups = [self.particles]

    def draw(self, surface: Surface, debug: bool = False):
        # todo: this is to make child particles appear behind self. Need to make it so I can
        #  configure this without hacking.
        super().draw(surface, debug)
        surface.blit(self.image, self.image_rect)

    def state_idle(self):
        if mouse_hovering_over(self):
            self.smoke()
            # if EventQueue.filter(pygame.MOUSEBUTTONDOWN):
            #     self.spark()
            #     self.state = self.state_grabbed

    def state_grabbed(self):
        self.flame()
        self.rect.center = pygame.mouse.get_pos()
        if EventQueue.filter(pygame.MOUSEBUTTONUP):
            # snap to nearest square
            squares = pygame.sprite.spritecollide(self, self.board.squares, dokill=False)
            nearest_square = min(squares, key=lambda s: distance(s, self))
            self.rect.center = nearest_square.rect.center
            self.state = self.state_idle

            # kill any other pieces on that square
            pieces = pygame.sprite.spritecollide(self, self.board.pieces, dokill=False)
            for piece in pieces:
                if piece is not self:
                    piece.kill()

    def spark(self):
        for _ in range(20):
            self.particles.add(
                Particle(
                    x=self.x + random_int(-5, 5),
                    y=self.y + random_int(-5, 5),
                    u=1 * random_float(-15, 15),
                    v=1 * random_float(-15, 15),
                    radius=random_int(5, 12),
                    color=(200, 200, 150),
                    gravity=0.1,
                    decay=0.2,
                    friction=0.1,
                )
            )

    def smoke(self):
        self.particles.add(
            Particle(
                self.x + random_float(-15, 15),
                self.y + random_float(-15, 15),
                u=0 + random_float(-1, 1),
                v=-3 + random_float(-5, 5),
                radius=random_int(12, 25),
                color=self.flame_color,
                gravity=-0.02,
                friction=0.025,
                blit_flag=pygame.BLEND_SUB,
                decay=1.5,
            )
        )

    @property
    def flame_color(self):
        return (
            (
                random_int(0, 80),
                random_int(0, 15),
                random_int(0, 100),
            )
            if self.team == BLACK
            else (
                random_int(0, 60),
                random_int(0, 60),
                random_int(0, 10),
            )
        )

    def flame(self):
        self.particles.add(
            Particle(
                self.x,
                self.y,
                u=30 * 0 + random_float(-5, 5),
                v=30 * 0 + random_float(-5, 5),
                radius=random_int(30, 60),
                color=self.flame_color,
                gravity=-0.5,
                decay=1,
                friction=0.1,
                blit_flag=pygame.BLEND_SUB,
            )
        )


class Pawn(GuiPiece):
    sprite_name = "pawn"


class Queen(GuiPiece):
    sprite_name = "queen"


class King(GuiPiece):
    sprite_name = "king"


class Bishop(GuiPiece):
    sprite_name = "bishop"


class Rook(GuiPiece):
    sprite_name = "rook"


class Knight(GuiPiece):
    sprite_name = "knight"
