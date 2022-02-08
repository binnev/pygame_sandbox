import random

from pygame.rect import Rect
from base.objects import Entity, PhysicalEntity, Group
from base.stuff.gui_test import mouse_hovering_over
from chess import conf
from pygame import Surface, Color

from chess.constants import BLACK, WHITE
from chess.gui.classes.piece import Pawn, King, Queen, Bishop, Knight, Rook


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
