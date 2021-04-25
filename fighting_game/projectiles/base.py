from pygame.rect import Rect

from fighting_game.objects import PhysicalEntity


class Projectile(PhysicalEntity):
    owner: "Character"
    level: "Level"
    active_hitboxes: list  # subclasses should add/remove hitboxes from this list
    width: int
    height: int

    def __init__(self, x, y, u, v, owner):
        super().__init__()
        self.rect = Rect(0, 0, self.width, self.height)
        self.x = x
        self.y = y
        self.u = u
        self.v = v
        self.owner = owner
        self.state = self.state_main

    def state_main(self):
        # move
        self.x += self.u
        self.y += self.v

        # add hitboxes every tick
        for hitbox in self.active_hitboxes:
            self.level.add_hitbox(hitbox)

    def enter_hitpause(self):
        pass
