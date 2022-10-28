import pygame
from robingame.objects import Entity, Group

from slappers_only import sounds
from slappers_only.objects import Character


class SlappersOnlyScene(Entity):
    def __init__(self):
        super().__init__()
        self.characters = Group()
        self.characters.add(Character(x=100, y=100))
        self.characters.add(Character(x=180, y=100, facing_right=False))

        self.child_groups = [
            self.characters,
        ]

    def update(self):
        super().update()
        p1, p2 = self.characters
        collision = pygame.sprite.collide_mask(p1, p2)
        if collision:
            if p1.state.__name__ == p2.state.__name__ == "state_slap":
                p1.state = p1.state_idle
                p2.state = p2.state_idle
                sounds.metal_clang.play()
                print("clang")
            if p1.state.__name__ == "state_slap" and p2.state.__name__ != "state_get_hit":
                p2.state = p2.state_get_hit
                sounds.slap2.play()
            if p2.state.__name__ == "state_slap" and p1.state.__name__ != "state_get_hit":
                p1.state = p1.state_get_hit
                sounds.slap2.play()

            print("collision")
