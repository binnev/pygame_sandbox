import pygame
from robingame.objects import Game

from slappers_only import sounds
from slappers_only.objects import Character


class SlappersOnly(Game):
    window_width = 1000
    window_height = 500
    window_caption = "Slappers Only"
    screen_color = (255, 255, 255)
    fps=60

    def __init__(self):
        super().__init__()
        self.scenes.add(Character(x=100, y=100))
        self.scenes.add(Character(x=180, y=100, facing_right=False))

    def update(self):
        super().update()
        p1, p2 = self.scenes
        collision = pygame.sprite.collide_mask(p1, p2)
        if collision:
            if p1.state.__name__ == p2.state.__name__ == "state_slap":
                p1.state = p1.state_idle
                p2.state = p2.state_idle
                sounds.metal_clang.play()
            if p1.state.__name__ == "state_slap" and p2.state.__name__ != "state_get_hit":
                p2.state = p2.state_get_hit
                sounds.slap2.play()
            if p2.state.__name__ == "state_slap" and p1.state.__name__ != "state_get_hit":
                p1.state = p1.state_get_hit
                sounds.slap2.play()

            print("collision")


if __name__ == "__main__":
    SlappersOnly().main()
