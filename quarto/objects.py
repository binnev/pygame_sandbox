import pygame
from pygame import Surface, Rect
from pygame.color import Color
from pygame.sprite import AbstractGroup

from base.animation import recolor_image, scale_image
from base.objects import PhysicalEntity, Entity, Group
from base.utils import maskFromSurface, mask_to_surface, outline_image
from fighting_game.particles import Particle, random_float, random_int
from quarto.assets.images import quarto_pieces, misc
from quarto.utils import common_attribute


class Piece(PhysicalEntity):
    tall: bool
    hollow: bool
    square: bool
    black: bool

    mouse_offset: tuple
    board_square: "Square" = None
    highlight = True

    def __init__(self, x: int, y: int, tall: bool, hollow: bool, square: bool, black: bool):
        super().__init__()
        self.rect = Rect(0, 0, 64, 110 if tall else 80)
        self.rect.center = (x, y)
        self.tall = tall
        self.hollow = hollow
        self.square = square
        self.black = black
        image_code = f"{self.height}-{self.tip}-{self.shape}-white"
        self.image = quarto_pieces[image_code].play(0)
        if self.black:
            self.image = recolor_image(
                self.image,
                {
                    (119, 119, 119): (30, 30, 30),
                    (142, 142, 142): (40, 40, 40),
                    (176, 176, 176): (50, 50, 50),
                    (255, 255, 255): (100, 100, 100),
                },
            )
        self.particles = Group()
        self.child_groups = [self.particles]

    def state_main(self):
        pass

    def state_grabbed(self):
        mx, my = pygame.mouse.get_pos()
        dx, dy = self.mouse_offset
        self.rect.center = ((mx + dx), (my + dy))

    def draw(self, surface: Surface, debug: bool = False):
        if self.highlight:
            outline = outline_image(self.image)
            img_rect = self.image_rect
            outline = [(x + img_rect.x, y + img_rect.y) for x, y in outline]
            pygame.draw.polygon(surface, Color("red"), outline, 20)
        self.highlight = False
        surface.blit(self.image, self.image_rect)
        super().draw(surface, debug)

    @property
    def image_rect(self):
        if self.image:
            image_rect = self.image.get_rect()
            image_rect.center = self.rect.center
            image_rect.bottom = self.rect.bottom
            return image_rect
        else:
            return None

    @property
    def height(self):
        return "tall" if self.tall else "short"

    @property
    def colour(self):
        return "black" if self.black else "white"

    @property
    def tip(self):
        return "hollow" if self.hollow else "solid"

    @property
    def shape(self):
        return "square" if self.square else "round"

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
            )
        )


class Square(PhysicalEntity):
    width = 60
    height = 30
    piece: Piece = None

    def __init__(self, x, y, black: bool, *groups: AbstractGroup) -> None:
        super().__init__(*groups)
        self.rect = Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)

        self.black = black
        self.image = misc["square"].play(0)
        if self.black:
            self.image = recolor_image(self.image, {(255, 255, 255): (100, 100, 100)})

        self.pieces = Group()
        self.child_groups = [self.pieces]

    def add_piece(self, piece: Piece):
        piece.rect.midbottom = self.rect.midbottom
        self.piece = piece
        piece.board_square = self

    def remove_piece(self, piece):
        self.piece = None
        piece.board_square = None


class QuartoBoard(Entity):
    def __init__(self, x, y, *groups: AbstractGroup) -> None:
        super().__init__(*groups)
        self.x = x
        self.y = y
        self.squares = Group()
        self.pieces = Group()
        self.child_groups = [
            self.squares,
            self.pieces,
        ]
        self.square_coords = {}

        self.win_vectors = [
            # columns
            ((0, 0), (0, 1), (0, 2), (0, 3)),
            ((1, 0), (1, 1), (1, 2), (1, 3)),
            ((2, 0), (2, 1), (2, 2), (2, 3)),
            ((3, 0), (3, 1), (3, 2), (3, 3)),
            # rows
            ((0, 0), (1, 0), (2, 0), (3, 0)),
            ((0, 1), (1, 1), (2, 1), (3, 1)),
            ((0, 2), (1, 2), (2, 2), (3, 2)),
            ((0, 3), (1, 3), (2, 3), (3, 3)),
            # diagonals
            ((0, 0), (1, 1), (2, 2), (3, 3)),
            ((3, 0), (2, 1), (1, 2), (0, 3)),
        ]

        for ii in range(16):
            y, x = divmod(ii, 4)
            SPACING = 60
            screen_x = self.x + (x + y) * SPACING
            screen_y = self.y + (y - x) * SPACING // 2
            sq = Square(screen_x, screen_y, black=(y % 2) == (x % 2))
            self.squares.add(sq)
            self.square_coords[(x, y)] = sq

        self.state = self.state_main

    def state_main(self):
        self.check_victory()

    def draw(self, surface: Surface, debug: bool = False):
        for square in self.squares_forward():
            square.draw(surface, debug)
        for square in self.squares_forward():
            if square.piece:
                square.piece.draw(surface, debug)

    def squares_forward(self):
        for ii in range(16):
            y, x = divmod(ii, 4)
            yield self.square_coords[(x, y)]

    def squares_backward(self):
        for ii in range(15, -1, -1):
            y, x = divmod(ii, 4)
            yield self.square_coords[(x, y)]

    def pieces_backward(self):
        for square in self.squares_backward():
            if square.piece:
                yield square.piece

    def check_victory(self):
        for vector in self.win_vectors:
            pieces = [piece for xy in vector if (piece := self.square_coords[xy].piece)]
            if len(pieces) < 4:
                continue
            if common_attribute(pieces):
                for piece in pieces:
                    piece.highlight = True
                break


class UnusedPiecePad(PhysicalEntity):
    width = 300
    height = 150

    def __init__(self, x, y, *groups: AbstractGroup) -> None:
        super().__init__(*groups)
        self.rect = Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.image = misc["square"].play(0)
        self.image = scale_image(self.image, 4)
