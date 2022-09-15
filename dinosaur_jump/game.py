from pygame import Surface

from base.objects import Game, Group
from base.text.font import fonts
from dinosaur_jump import images
from dinosaur_jump.objects.background import ScrollingBackground
from dinosaur_jump.objects.characters import Dino, Ptero


class DinoJump(Game):
    window_width = 1000
    window_height = 500
    window_caption = "Dino Jump"
    screen_color = (130, 130, 130)

    def __init__(self):
        super().__init__()
        self.entities = Group()
        self.background = Group()
        self.child_groups = [
            self.background,
            self.entities,
        ]
        self.entities.add(Dino(x=100, y=450))
        self.entities.add(Ptero(x=self.window_width+16-100, y=150))
        self.background.add(ScrollingBackground(0, 250, images.mountains2, speed=5))
        self.background.add(ScrollingBackground(0, 250, images.mountains1, speed=10))
        self.background.add(ScrollingBackground(0, 250, images.grass, speed=20))

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        fonts.cellphone_white.render(
            surface, "Dino Jump", x=0, y=0, wrap=self.window_width, align=0, scale=5
        )


if __name__ == "__main__":
    DinoJump().main()
