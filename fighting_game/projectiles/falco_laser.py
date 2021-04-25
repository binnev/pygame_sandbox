from pygame import Color, Surface

from fighting_game import sounds
from fighting_game.hitboxes import Hitbox
from fighting_game.projectiles.base import Projectile


class FalcoLaserHitbox(Hitbox):
    def handle_hit(self, object):
        super().handle_hit(object)
        self.owner.kill()  # delete on hit


class FalcoLaser(Projectile):
    width = 150
    height = 10
    speed = 20

    def __init__(self, x, y, facing_right, owner):
        u = self.speed if facing_right else -self.speed
        super().__init__(x=x, y=y, u=u, v=0, owner=owner)
        self.image = Surface((150, 10))
        self.image.fill(Color("red"))
        self.active_hitboxes = [
            FalcoLaserHitbox(
                owner=self,
                x_offset=x_offset,
                width=30,
                height=30,
                base_knockback=20,
                knockback_angle=30,
                damage=3,
                sound=sounds.hit_electric2,
            )
            for x_offset in [-75, 0, 75]
        ]

    def handle_hit(self, hitbox):
        self.kill()
