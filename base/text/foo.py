import string
from pathlib import Path

from pygame.color import Color
from pygame.surface import Surface

from base.image import load_spritesheet, scale_image
from base.objects import Game

code_snippet = """
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

    def __init__(self, filename: str | Path, image_size=None, letters: str = None):
        """`letters` is the letters in the spritesheet, in the same order."""
        self.image_size = image_size
        self.letters = dict()
        self.letters[" "] = Surface(image_size)
        self.not_found = Surface(image_size)
        self.not_found.fill(Color("red"))
        letters = letters or string.ascii_uppercase + string.ascii_lowercase
        filename = Path(filename)
        images = load_spritesheet(filename, image_size=image_size)
        self.letters.update({letter: image for letter, image in zip(letters, images)})

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

    def get(self, letter: str) -> Surface:
        try:
            return self.letters[letter]
        except KeyError:
            return self.not_found


class FontTest(Game):
    window_width = 1500
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
        )

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        self.font.render(surface, code_snippet)


if __name__ == "__main__":
    FontTest().main()
