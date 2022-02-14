import pygame
from pygame import Surface, Color
from pygame.rect import Rect

from base.input import EventQueue
from base.objects import Entity, PhysicalEntity, Group
from base.stuff.gui_test import mouse_hovering_over
from chess import conf
from chess.engine.classes.board import ChessBoard
from chess.gui.classes.piece import (
    GuiPiece,
    CLASSES_BY_LETTER,
)
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

        # font = pygame.font.Font(pygame.font.get_default_font(), 20)
        # text = font.render(f"{self.coords[0]}, {self.coords[1]}", True, Color("red"))
        # textRect = text.get_rect()
        # textRect.bottomleft = image.get_rect().bottomleft
        # image.blit(text, textRect)

        return image


class SquareAnnotation(PhysicalEntity):
    width = conf.SQUARE_SIZE
    height = conf.SQUARE_SIZE
    color: Color = (30, 30, 30, 30)

    def __init__(self, x, y, *groups):
        super().__init__(*groups)
        self.rect = Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        pygame.draw.circle(surface, self.color, self.rect.center, conf.SQUARE_SIZE // 3, 5)


class GuiBoard(Entity):
    parental_name = "board"

    def __init__(self, *groups):
        super().__init__(*groups)
        self.squares = Group()
        self.pieces = Group()
        self.selected_pieces = Group()
        self.annotations = Group()
        self.child_groups = [
            self.squares,
            self.annotations,
            self.pieces,
            self.selected_pieces,
        ]
        self.state = self.state_idle
        self.square_coords = dict()

        for x in range(8):
            for y in range(8):
                color = (40, 40, 40) if (y % 2) == (x % 2) else (90, 90, 90)
                screen_x = (x + 1) * conf.SQUARE_SIZE
                screen_y = conf.SQUARE_SIZE * 10 - (y + 1) * conf.SQUARE_SIZE
                square = GuiSquare(screen_x, screen_y, (x, y), color)
                self.add_squares(square)
                self.square_coords[(x, y)] = square

        self.engine = ChessBoard()
        self.engine.load_standard_setup()
        self.load_engine_position()

    def load_engine_position(self):
        for coords, engine_piece in self.engine.contents.items():
            klass = CLASSES_BY_LETTER[engine_piece.letter]
            piece = klass(0, 0, engine_piece.team)
            self.add_piece_to_square(piece, coords)

    def add_piece_to_square(self, piece, coords):
        square = self.square_coords[coords]
        piece.rect.center = square.rect.center
        piece.square = square
        self.add_pieces(piece)

    def add_squares(self, *objects):
        self.add_to_group(*objects, group=self.squares)

    def add_pieces(self, *objects):
        self.add_to_group(*objects, group=self.pieces)

    def add_annotations(self, *objects):
        self.add_to_group(*objects, group=self.annotations)

    def pick_up(self, piece: GuiPiece):
        self.annotations.kill()
        piece.state = piece.state_grabbed
        self.selected_pieces.add(piece)
        self.pieces.remove(piece)
        # add annotations for piece's legal moves
        annotations = []
        for _, destination in self.get_legal_moves(piece):
            square = self.square_coords[destination]
            annotation = SquareAnnotation(square.x, square.y)
            annotations.append(annotation)
        self.add_annotations(*annotations)

    def state_idle(self):
        if EventQueue.filter(pygame.MOUSEBUTTONDOWN):
            for piece in self.pieces:
                if mouse_hovering_over(piece):
                    self.pick_up(piece)
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

    def get_legal_moves(self, piece: GuiPiece):
        return self.engine.piece_legal_moves(piece.square.coords)
