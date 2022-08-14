import string
from pathlib import Path

from pygame.color import Color
from pygame.surface import Surface

from base.image import load_spritesheet, scale_image
from base.objects import Game

"""
todo:
- auto-wrap at width 
- trim (un-monospace) characters
"""
snippet = """
def render(self, surf: Surface, text: str, x: int = 0, y: int = 0, scale: int = 1) -> Surface:
    lines = text.splitlines()
    for line in lines:
        cursor = x
        for letter in line:
            image = self.get(letter)
            image = scale_image(image, scale)
            surf.blit(image, (cursor, y))
            cursor += self.image_size[0] * scale
        y += self.image_size[1] * scale
    return surf
"""


class Font:
    letters: dict[str:Surface]
    image_size: tuple[int, int]
    xpad: int
    ypad: int

    def __init__(
        self,
        filename: str | Path,
        image_size: tuple[int, int],
        letters: str = None,
        xpad=0,
        ypad=0,
        trim=False,
        **kwargs,
    ):
        """`letters` is the letters in the spritesheet, in the same order."""
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
        if trim:
            images = self.trim_images(images)
        self.letters.update({letter: image for letter, image in zip(letters, images)})

    def render(self, surf: Surface, text: str, x: int = 0, y: int = 0, scale: int = 1) -> Surface:
        for line in text.splitlines():
            cursor = x
            for letter in line:
                image = self.get(letter)
                image = scale_image(image, scale)
                surf.blit(image, (cursor, y))
                w = image.get_width()
                cursor += w + self.xpad * scale
            y += (self.ysize + self.ypad) * scale
        return surf

    def trim_images(self, images: list[Surface]) -> list[Surface]:
        trimmed = []
        for image in images:
            x, _, w, _ = image.get_bounding_rect()  # trim x to bounding rect
            _, y, _, h = image.get_rect()  # maintain original y position of character
            new = image.subsurface((x, y, w, h))
            trimmed.append(new)
        return trimmed

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
            trim=True,
            xpad=1
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
            xpad=1,
            colorkey=-1,
            trim=True,
        )

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        self.cellphone.render(surface, snippet, scale=2)


if __name__ == "__main__":
    FontTest().main()
