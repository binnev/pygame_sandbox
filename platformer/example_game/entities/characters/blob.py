from pathlib import Path
import numpy
import pygame

from platformer.objects.entities import Character, Keys, Entity, AnimationMixin, \
    PhysicsMixin, CollisionMixin, Projectile

from platformer.objects.animation import SpriteAnimation, SpriteSheet
from ...conf import SCALE_SPRITES

folder = Path("sprites/blob/")
# todo; make a class for this. SpriteSet?
BLOB_SPRITES = {
    "stand":
        SpriteAnimation(
            SpriteSheet((folder / "blob_stand.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES)),
    "jump":
        SpriteAnimation(
            SpriteSheet((folder / "blob_jump.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3)),
    "jump_right":
        SpriteAnimation(
            SpriteSheet((folder / "blob_jump_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3)),
    "jump_left":
        SpriteAnimation(SpriteSheet(
            (folder / "blob_jump_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3),
                        flip_horizontal=True),
    "fall":
        SpriteAnimation(
            SpriteSheet((folder / "blob_fall.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3)),
    "fall_right":
        SpriteAnimation(
            SpriteSheet((folder / "blob_fall_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3)),
    "fall_left":
        SpriteAnimation(SpriteSheet(
            (folder / "blob_fall_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3),
                        flip_horizontal=True),
    "crouch":
        SpriteAnimation(SpriteSheet(
            (folder / "blob_crouch.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES),
                        looping=False),
    "run_right":
        SpriteAnimation(
            SpriteSheet((folder / "blob_run_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=8)),
    "run_left":
        SpriteAnimation(SpriteSheet(
            (folder / "blob_run_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=8),
                        flip_horizontal=True),
}

folder = Path("sprites/blob/")
PROJECTILE_SPRITES = {
    "right":
        SpriteAnimation(
            SpriteSheet((folder / "blob_projectile.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES)),
    "left":
        SpriteAnimation(SpriteSheet(
            (folder / "blob_projectile.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES),
                        flip_horizontal=True),
}

folder = Path("sprites/volleyball/")
BALL_SPRITES = {
    "default":
        SpriteAnimation(
            SpriteSheet((folder / "volleyball.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES)),
}


class Blob(Character):

    width = 80
    height = 70
    _state = None
    ground_acceleration = 10
    ground_speed = 9
    air_acceleration = 2
    air_speed = 6
    gravity = 1.2
    _fall_speed = 5
    fastfall_multiplier = 2.5
    aerial_jumps = 3
    jump_power = 20
    jumpsquat_frames = 4
    _friction = 0.3
    air_resistance = 0.05
    crouch_height_multiplier = .7

    # cooldowns -- todo: put this in a mixin?
    double_jump_cooldown_frames = 15  # should this go in the Character class?
    double_jump_cooldown = 0
    projectile_cooldown_frames = 30
    projectile_cooldown = 0

    # put these in a subclass
    sprites = BLOB_SPRITES
    image = sprites["stand"].get_frame(0)

    def __init__(self, x, y, groups=[]):
        """Extend parent init method here e.g. by adding extra entries to the
        state_lookup dict"""
        super().__init__(x, y, groups)
        self.states.SHOOT_PROJECTILE = "SHOOT_PROJECTILE"
        self.state_lookup.update(
            {self.states.SHOOT_PROJECTILE: self.state_shoot_projectile})

    def update_cooldowns(self):
        super().update_cooldowns()
        if self.projectile_cooldown:
            self.projectile_cooldown -= 1

    # ============ state functions ================

    def state_fall(self):
        """Extends parent class state_fall by allowing shooting projectiles"""
        super().state_fall()
        if self.keys[Keys.FIRE] and not self.projectile_cooldown:
            self.state = self.states.SHOOT_PROJECTILE

    def state_shoot_projectile(self):
        # image
        self.image = self.sprites["stand"].get_frame(self.frames_elapsed)
        old_width = self.image.get_rect().width
        old_height = self.image.get_rect().height
        self.image = pygame.transform.scale(self.image,
                                            (int(old_width * 0.5), old_height))
        self.allow_fastfall()
        self.enforce_max_fall_speed()

        if self.frames_elapsed == 10:  # todo: don't hard-code this
            self.create_projectile()
        if self.frames_elapsed == 12:
            self.state = self.states.FALL if self.airborne else self.states.STAND

    # ============ actions ==============

    def create_projectile(self):
        if self.keys[Keys.RIGHT]:
            facing = "right"
        elif self.keys[Keys.LEFT]:
            facing = "left"
        else:
            facing = "right" if self.u > 0 else "left"
        self.level.add_objects(
            BlobProjectile(*self.centroid, 100, 100, facing=facing))
        self.projectile_cooldown = self.projectile_cooldown_frames


class BlobProjectile(Projectile):
    sprites = PROJECTILE_SPRITES
    speed = 7


class Ball(Entity, AnimationMixin, PhysicsMixin, CollisionMixin):
    width = 50
    height = 50
    sprites = BALL_SPRITES
    image = sprites["default"].get_frame(0)
    BOUNCINESS = 3
    GRAVITY = .5
    AIR_RESISTANCE = 0.01

    def __init__(self, x, y, groups=[], color=None):
        super().__init__(x, y, self.width, self.height, groups=groups)

    def update(self, keys):
        self.handle_collisions()
        self.update_physics()
        self.update_animation()
        self.enforce_screen_limits()

    def handle_collisions(self):
        collision_object_lists = (
            # self.level.platforms,
            self.level.characters,)
        for collision_object_list in collision_object_lists:
            collided_objects = pygame.sprite.spritecollide(
                self, collision_object_list, dokill=False)
            for collided_object in collided_objects:
                # bounce self away from collided object
                print(f"collided with {collided_object}")
                delta_x = self.centroid.x - collided_object.centroid.x
                delta_y = self.centroid.y - collided_object.centroid.y
                vector = numpy.array([delta_x, delta_y])
                magnitude = numpy.sqrt(delta_x**2 + delta_y**2)
                unit_vector = vector / magnitude
                self.u += unit_vector[0] * self.BOUNCINESS
                self.v += unit_vector[1] * self.BOUNCINESS
                # prevent overlapping
                self.collide_solid_platform(collided_object)

    def enforce_screen_limits(self, screen_width, screen_height):
        if self.rect.left < 0:
            self.rect.left = 0
            self.u *= -1
        if self.rect.right > screen_width:
            self.rect.right = screen_width
            self.u *= -1
        if self.rect.top < 0:
            self.rect.top = 0
            self.v *= -1
        if self.rect.bottom > screen_width:
            self.rect.bottom = screen_width
            self.v *= -1

    def update_physics(self):
        # update position
        self.x += self.u
        self.y += self.v

        self.v += self.GRAVITY

        self.u *= (1 - self.AIR_RESISTANCE)  # air resistance
        self.v *= (1 - self.AIR_RESISTANCE)  # air resistance

        # don't allow sub-pixel speeds
        self.u = 0 if abs(self.u) < .5 else self.u