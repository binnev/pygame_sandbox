import math
import random

import pygame
from pygame import Surface, Color
from pygame import Vector2
from pygame.rect import Rect

from base.input import EventQueue
from base.objects import Entity, PhysicalEntity, Group
from base.stuff.gui_test import mouse_hovering_over
from chess import conf
from chess.constants import BLACK, WHITE
from chess.gui.classes.piece import Pawn, King, Queen, Bishop, Knight, Rook, GuiPiece
from chess.gui.utils import distance


class GuiSquare(PhysicalEntity):
    width = conf.SQUARE_SIZE
    height = conf.SQUARE_SIZE
    color: Color

    def __init__(self, x, y, coords, color: Color, *groups):
        """
        :param x: screen x
        :param y: screen y
        :param coords: coordinates for the engine
        :param groups:
        """
        super().__init__(*groups)
        self.rect = Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.color = color
        self.coords = coords

    @property
    def image(self):
        image = Surface((self.width - 5, self.height - 5))
        if mouse_hovering_over(self):
            image.fill((160, 160, 130))
        else:
            image.fill(self.color)

        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        text = font.render(f"{self.coords[0]}, {self.coords[1]}", True, Color("red"))
        textRect = text.get_rect()
        textRect.bottomleft = image.get_rect().bottomleft
        image.blit(text, textRect)

        return image


class GuiBoard(Entity):
    parental_name = "board"

    def __init__(self, *groups):
        super().__init__(*groups)
        self.squares = Group()
        self.pieces = Group()
        self.selected_pieces = Group()
        self.child_groups = [self.squares, self.pieces, self.selected_pieces]
        self.state = self.state_idle

        for x in range(8):
            for y in range(8):
                color = (40, 40, 40) if (y % 2) == (x % 2) else (90, 90, 90)
                screen_x = (x + 1) * conf.SQUARE_SIZE
                screen_y = conf.SQUARE_SIZE * 10 - (y + 1) * conf.SQUARE_SIZE
                sq = GuiSquare(screen_x, screen_y, (x, y), color)
                self.add_squares(sq)

                # # add random pieces
                # klass = random.choice([Pawn, King, Queen, Bishop, Knight, Rook])
                # team = random.choice([WHITE, BLACK])
                # piece = klass(screen_x, screen_y, team)
                # self.add_pieces(piece)

    def add_squares(self, *objects):
        self.add_to_group(*objects, group=self.squares)

    def add_pieces(self, *objects):
        self.add_to_group(*objects, group=self.pieces)

    def state_idle(self):
        if EventQueue.filter(pygame.MOUSEBUTTONDOWN):
            for piece in self.pieces:
                piece: GuiPiece
                if mouse_hovering_over(piece):
                    piece.state = piece.state_grabbed
                    self.selected_pieces.add(piece)
                    self.pieces.remove(piece)
                    break  # only one piece at a time

        if EventQueue.filter(pygame.MOUSEBUTTONUP):
            for piece in self.selected_pieces:
                piece.state = piece.state_idle

                # snap to nearest square
                nearest_sq = min(self.squares, key=lambda s: distance(s, piece))
                piece.rect.center = nearest_sq.rect.center

                # remove other pieces on that square
                capture = pygame.sprite.spritecollide(piece, self.pieces, dokill=True)
                if capture:
                    piece.blood()

                self.selected_pieces.remove(piece)
                self.pieces.add(piece)
