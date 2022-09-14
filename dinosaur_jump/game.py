from base.objects import Game, Group
from dinosaur_jump import images
from dinosaur_jump.objects.background import ScrollingBackground
from dinosaur_jump.objects.dino import Dino


class DinoJump(Game):
    window_width = 1000
    window_height = 500
    window_caption = "Dino Jump"
    screen_color = (130, 130, 130)

    def __init__(self):
        super().__init__()
        self.entities = Group()
        self.background = Group()
        self.child_groups.append(self.background)
        self.child_groups.append(self.entities)
        self.entities.add(Dino(x=100, y=450))
        self.background.add(ScrollingBackground(0, 250, images.mountains2, speed=5))
        self.background.add(ScrollingBackground(0, 250, images.mountains1, speed=10))
        self.background.add(ScrollingBackground(0, 250, images.grass, speed=20))



if __name__ == "__main__":
    DinoJump().main()