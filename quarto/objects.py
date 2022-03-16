from pygame import Surface, Rect, Color

from base.animation import recolor_image
from base.objects import PhysicalEntity
from quarto.assets.pieces import quarto_pieces


class Piece(PhysicalEntity):
    tall: bool
    hollow: bool
    square: bool
    black: bool

    def __init__(self, x: int, y: int, tall: bool, hollow: bool, square: bool, black: bool):
        super().__init__()
        self.rect = Rect(0, 0, 32, 32)
        self.rect.center = (x, y)
        self.tall = tall
        self.hollow = hollow
        self.square = square
        self.black = black
        image_code = f"{self.height}-{self.tip}-{self.shape}-white"
        try:
            self.image = quarto_pieces[image_code].play(0)
        except KeyError:
            self.image = Surface((50, 50))
            self.image.fill(Color("red"))  # 119
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
