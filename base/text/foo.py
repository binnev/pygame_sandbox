import string
from pathlib import Path

from pygame.color import Color
from pygame.surface import Surface

from base.image import load_spritesheet, scale_image
from base.objects import Game

snippet = """
De bekendste voorbeelden zitten in de bandnamen Motörhead, Blue Öyster Cult, 
Mötley Crüe en Queensrÿche. Dit gebruik werd geparodieerd door de groep Spin̈al Tap, 
die een umlaut op de medeklinker n plaatste. (Een n met umlaut komt in een beperkt aantal talen 
voor: het Jacalteeks en het Malagasy. Het is echter hoogst onwaarschijnlijk dat de leden van 
Spin̈al Tap dit wisten.) 

Het is tevens de achternaam van de fictieve Lars Ümlaüt uit Guitar Hero III: Legends of Rock.
"""


class Font:
    letters: dict[str:Surface]
    image_size: tuple[int, int]
    xpad: int
    ypad: int

    def __init__(
        self, filename: str | Path, image_size, letters: str = None, xpad=0, ypad=0, **kwargs
    ):
        """`letters` is the letters in the spritesheet, in the same order."""
        print(kwargs)
        self.image_size = image_size
        self.xpad = xpad
        self.ypad = ypad
        self.letters = dict()
        space = Surface(image_size).convert_alpha()
        space.fill((0, 0, 0, 0))
        self.letters[" "] = space
        self.not_found = Surface(image_size)
        self.not_found.fill(Color("red"))
        letters = letters or string.ascii_uppercase + string.ascii_lowercase
        filename = Path(filename)
        images = load_spritesheet(filename, image_size=image_size, **kwargs)
        print(f"{len(images)=}")
        self.letters.update({letter: image for letter, image in zip(letters, images)})

    def render(self, surf: Surface, text: str, x: int = 0, y: int = 0, scale: int = 1) -> Surface:
        for line in text.splitlines():
            cursor = x
            for letter in line:
                image = self.get(letter)
                image = scale_image(image, scale)
                surf.blit(image, (cursor, y))
                cursor += (self.xsize + self.xpad) * scale
            y += (self.ysize + self.ypad) * scale
        return surf

    def get(self, letter: str) -> Surface:
        try:
            return self.letters[letter]
        except KeyError:
            return self.not_found

    @property
    def xsize(self):
        return self.image_size[0]

    @property
    def ysize(self):
        return self.image_size[1]


class FontTest(Game):
    window_width = 1500
    screen_color = (150, 150, 150)

    def __init__(self):
        super().__init__()
        filename = Path(__file__).parent / "assets/test_font.png"
        assert filename.exists()
        self.font = Font(
            filename=filename,
            image_size=(16, 16),
            letters=(
                string.ascii_uppercase
                + string.ascii_lowercase
                + "1234567890-=!@#$%^&*()_+[]\;',./{}|:\"<>?~`"
            ),
            xpad=-9,
        )
        filename = Path(__file__).parent / "assets/charmap-cellphone_white.png"
        assert filename.exists()
        self.cellphone = Font(
            filename=filename,
            image_size=(7, 9),
            letters=(
                """!"#$%&'()*+,-./0123456789:'<=>?@"""
                + string.ascii_uppercase
                + "[\]^_`"
                + string.ascii_lowercase
                + "{|}~"
            ),
            xpad=-2,
            colorkey=-1,
        )

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        self.cellphone.render(surface, snippet, scale=2)


if __name__ == "__main__":
    FontTest().main()
