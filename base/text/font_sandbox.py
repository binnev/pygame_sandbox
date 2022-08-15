import string
from pathlib import Path

import pygame.draw
from pygame.color import Color
from pygame.surface import Surface

from base.objects import Game
from base.text.font import Font

snippet = """
Ook in de spelling van sommige andere talen wordt de umlaut gebruikt, bijvoorbeeld in verwante talen als het IJslands en het Zweeds, om een soortgelijk 

klankverschijnsel
weer
te

geven, of in niet-verwante talen als het Fins, het Hongaars of het Turks, om dezelfde e-, eu- en u-klank weer te geven, die echter niet het resultaat van hetzelfde klankverschijnsel zijn.
""".strip()


class FontTest(Game):
    window_width = 1500
    screen_color = (150, 150, 150)

    def __init__(self):
        super().__init__()
        filename = Path(__file__).parent / "assets/test_font.png"
        self.font = Font(
            filename=filename,
            image_size=(16, 16),
            letters=(
                string.ascii_uppercase
                + string.ascii_lowercase
                + "1234567890-=!@#$%^&*()_+[]\;',./{}|:\"<>?~`"
            ),
            trim=True,
            xpad=1,
            space_width=8,
        )
        filename = Path(__file__).parent / "assets/charmap-cellphone_white.png"
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
            space_width=4,
        )

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        X = 500
        Y = 30
        WRAP = 500
        self.cellphone.render(
            surface,
            snippet,
            scale=2,
            wrap=WRAP,
            x=X,
            y=Y,
            align=-1,
        )
        pygame.draw.rect(surface, color=Color("red"), rect=(X, Y, WRAP, WRAP), width=1)


if __name__ == "__main__":
    FontTest().main()
