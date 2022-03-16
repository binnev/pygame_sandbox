import pygame
from pygame import Surface, Rect
from pygame.sprite import AbstractGroup

from base.animation import recolor_image
from base.objects import PhysicalEntity, Entity, Group
from quarto.assets.images import quarto_pieces, misc


class Piece(PhysicalEntity):
    tall: bool
    hollow: bool
    square: bool
    black: bool

    def __init__(self, x: int, y: int, tall: bool, hollow: bool, square: bool, black: bool):
        super().__init__()
        self.rect = Rect(0, 0, 64, 128 if tall else 64)
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

    def draw(self, surface: Surface, debug: bool = False):
        # todo: this is to make child particles appear behind self. Need to make it so I can
        #  configure this without hacking.
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


class Square(PhysicalEntity):
    width = 60
    height = 30

    def __init__(self, x, y, black: bool, *groups: AbstractGroup) -> None:
        super().__init__(*groups)
        self.rect = Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)

        self.black = black
        self.image = misc["square"].play(0)
        if self.black:
            self.image = recolor_image(self.image, {(255, 255, 255): (100, 100, 100)})


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

        ii = 0
        for tall in True, False:
            for hollow in True, False:
                for square in True, False:
                    for black in True, False:
                        y, x = divmod(ii, 4)
                        SPACING = 60
                        screen_x = self.x + (x + y) * SPACING
                        screen_y = self.y + (y - x) * SPACING // 2
                        sq = Square(screen_x, screen_y, black=(y % 2) == (x % 2))
                        self.squares.add(sq)
                        piece = Piece(
                                screen_x,
                                screen_y,
                                tall=tall,
                                hollow=hollow,
                                square=square,
                                black=black,
                            )
                        piece.rect.bottom = sq.rect.bottom
                        self.pieces.add(
                            piece,
                        )
                        ii += 1
