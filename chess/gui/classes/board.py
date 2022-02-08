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


class GuiSquare(PhysicalEntity):
    width = conf.SQUARE_SIZE
    height = conf.SQUARE_SIZE

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
        self.image = Surface((self.width - 5, self.height - 5))
        self.image.fill(color)
        self.color = color
        self.coords = coords
        self.state = self.state_idle

    def state_idle(self):
        if mouse_hovering_over(self):
            self.image.fill((160, 160, 130))
        else:
            self.image.fill(self.color)


class GuiBoard(Entity):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.squares = Group()
        self.pieces = Group()
        self.child_groups = [self.squares, self.pieces]
        self.state = self.state_idle

        for x in range(8):
            for y in range(8):
                color = (40, 40, 40) if (y % 2) == (x % 2) else (90, 90, 90)
                screen_x = (x + 1) * conf.SQUARE_SIZE
                screen_y = conf.SQUARE_SIZE * 10 - (y + 1) * conf.SQUARE_SIZE
                sq = GuiSquare(screen_x, screen_y, (x, y), color)
                self.add_squares(sq)
                klass = random.choice([Pawn, King, Queen, Bishop, Knight, Rook])
                team = random.choice([WHITE, BLACK])
                piece = klass(screen_x, screen_y, team)
                self.add_pieces(piece)

    def add_squares(self, *objects):
        self.add_to_group(*objects, group=self.squares)

    def add_pieces(self, *objects):
        self.add_to_group(*objects, group=self.pieces)

    def state_idle(self):
        if EventQueue.filter(pygame.MOUSEBUTTONDOWN):
            for piece in self.pieces:
                piece: GuiPiece
                if mouse_hovering_over(piece):
                    piece.spark()
                    piece.state = piece.state_grabbed
                    break  # only one piece at a time
        if EventQueue.filter(pygame.MOUSEBUTTONUP):
            for piece in self.pieces:
                if mouse_hovering_over(piece):
                    piece.state = piece.state_idle
                    squares = pygame.sprite.spritecollide(piece, self.squares, dokill=False)
                    nearest_square = min(squares, key=lambda s: distance(s, piece))
                    piece.rect.center = nearest_square.rect.center


def distance(obj1, obj2):
    dx = obj1.rect.centerx - obj2.rect.centerx
    dy = obj1.rect.centery - obj2.rect.centery
    return math.sqrt(dx**2 + dy**2)
