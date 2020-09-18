from collections import deque
from pathlib import Path

import numpy
import pygame as pygame
from numpy.core._multiarray_umath import sign

from base.animation import SpriteDict, SpriteAnimation
from base.objects.entities import Entity, CollisionMixin, Hitbox
from base.objects.mixins import HistoryMixin, AnimationMixin, PhysicsMixin
from base.utils import get_overlap_between_objects, un_overlap
from volleyball_game import conf
from volleyball_game.sprites.particle_effects import explosion_sprites
from volleyball_game.sprites.stickman import stickman_sprites
from volleyball_game.sprites.volleyball import volleyball_sprites


# todo: allow states to describe the rect dimensions when the entity is in that state. E.g.
#  during a dive the player's rect should be longer and thinner.
class VolleyballMove:
    sprite_animation_name: str
    sprite_animation: SpriteAnimation
    hitbox_mapping: dict  # mapping of frame keys to hitbox values
    left_and_right_versions: bool
    hitboxes: ["Hitbox"]
    active_hitboxes: ["Hitbox"]

    def __init__(self, instance):
        self.instance = instance
        # at instantiation, create flipped hitboxes.
        self.hitbox_mapping_flipped = {
            key: self.flip_hitboxes(hitboxes) for key, hitboxes in self.hitbox_mapping.items()
        }
        self.hitboxes = self.map_hitboxes(self.hitbox_mapping)
        self.hitboxes_flipped = self.map_hitboxes(self.hitbox_mapping_flipped)

    def __call__(self):
        """ This is the equivalent to the function states. """
        # fixme: convert to frames
        # flip sprite animation automatically
        name = self.sprite_animation_name + "_" + self.instance.facing
        self.sprite_animation = self.instance.sprites[name]

        frames_elapsed = self.instance.frames_elapsed
        self.image = self.sprite_animation.get_frame(frames_elapsed)

        # flip hitboxes automatically
        self.active_hitboxes = self.get_active_hitboxes(
            frames_elapsed, flip=not self.instance.facing_right
        )

        self.instance.image = self.image

        for hitbox in self.active_hitboxes:
            self.instance.level.add_hitbox(hitbox)

    @staticmethod
    def map_hitboxes(hitbox_mapping):
        # todo: allow some frames to have no hitboxes. How will I represent that?
        return {
            frame: hitboxes
            for frames, hitboxes in hitbox_mapping.items()
            for frame in ([frames] if isinstance(frames, int) else range(frames[0], frames[-1] + 1))
        }

    def get_active_hitboxes(self, n, flip):
        source = self.hitboxes if not flip else self.hitboxes_flipped
        return source.get(n, [])

    def end_when_animation_ends(self, next_state):
        if not self.sprite_animation.get_frame(self.instance.frames_elapsed + 1):
            self.instance.state = next_state

    def flip_hitboxes(self, hitboxes):
        return [hitbox.flip_x() for hitbox in hitboxes]


class Player(Entity, AnimationMixin, CollisionMixin, HistoryMixin):
    game_ticks_per_sprite_frame = conf.TICKS_PER_SPRITE_FRAME

    # class properties
    facing_right: bool
    width: int
    height: int
    _state: str
    ground_acceleration: float
    ground_speed: float
    air_acceleration: float
    air_speed: float
    dive_speed: float
    gravity: float
    _fall_speed: float
    fastfall_multiplier: float
    aerial_jumps: int
    jump_power: float
    shorthop_power: float
    jumpsquat_frames: int
    friction: float
    air_resistance: float
    crouch_height_multiplier: float

    # drawing
    sprites: SpriteDict
    image: pygame.Surface

    double_jump_cooldown_frames = 15
    double_jump_cooldown = 0

    # references to other objects
    level = None

    # historymixin
    attributes_to_remember = ["rect", "x", "y"]

    def __init__(self, x, y, facing_right=True, input=None, groups=[]):

        super().__init__(x, y, self.width, self.height, groups=groups)
        HistoryMixin.__init__(self)

        self.u = 0
        self.v = 0
        self.state = self.state_fall
        self.fastfall = False
        self.facing_right = facing_right
        self.input = input
        self.aerial_jumps_used = 0

    # ============== properties ==============

    @property
    def x(self):
        return self.rect.midbottom[0]

    @x.setter
    def x(self, new_x):
        self.rect.midbottom = new_x, self.rect.midbottom[1]

    @property
    def y(self):
        return self.rect.midbottom[1]

    @y.setter
    def y(self, new_y):
        self.rect.midbottom = self.rect.midbottom[0], new_y

    @property
    def rect(self):
        # todo: states should be responsible for this kind of thing
        # shrink rect when crouching
        midbottom = self._rect.midbottom
        if self.state in [self.state_squat, self.state_jumpsquat]:
            self._rect.height = self.height * self.crouch_height_multiplier
        else:
            self._rect.height = self.height
        self._rect.midbottom = midbottom
        return self._rect

    @rect.setter
    def rect(self, new_rect):
        self._rect = pygame.Rect(new_rect)

    @property
    def fall_speed(self):
        if self.fastfall:
            return self._fall_speed * self.fastfall_multiplier
        else:
            return self._fall_speed

    @property
    def airborne(self):
        for platform in self.level.platforms:
            if self.can_stand_on_platform(platform):
                return False
        return True

    @property
    def facing(self):
        return "right" if self.facing_right else "left"

    # ============== drawing functions ===============

    def align_image_rect(self):
        self.image_rect.midbottom = self.rect.midbottom

    # ============== main methods ====================

    def update(self):
        self.update_physics()
        self.state()
        self.enforce_screen_limits(*self.level.game.screen_size)
        # self.debug_print()
        self.update_cooldowns()
        self.update_animation()
        # fixme: I think this needs to be handled by the game class to prevent the
        #  order of object updates from fucking it up.
        self.update_history()

    def update_cooldowns(self):
        # todo: make a cooldowns mixin which does this for a list of cooldowns.
        if self.double_jump_cooldown:
            self.double_jump_cooldown -= 1

    def update_physics(self):

        self.handle_platform_collisions()

        # always apply gravity. Other functions can enforce max fall speed
        if self.airborne:
            self.v += self.gravity
        else:
            self.v = 0  # todo: I'm doing this multiple times
            self.aerial_jumps_used = 0  # reset double jump counter
            self.fastfall = False

        # reduce speeds
        if self.airborne:  # air resistance
            self.u = self.u - sign(self.u) * self.air_resistance
        else:  # friction
            self.u = self.u - sign(self.u) * self.friction
            self.v = 0

        self.x += self.u
        self.y += self.v

        # don't allow sub-pixel horizontal speeds. This prevents infinite sliding to
        # the left
        self.u = 0 if abs(self.u) < 0.2 else self.u

    # =========== utility methods ==================

    def debug_print(self):
        print(
            f"state = {self.state},",
            f"airborne = {self.airborne},",
            f"x = {self.x:.2f},",
            f"y = {self.y:.2f},",
            f"base.y = {self.base.y:.2f},",
            f"u = {self.u:.5f},",
            f"v = {self.v:.5f},",
            f"friction = {self.friction:.2f},",
            f"aerial_jumps_used = {self.aerial_jumps_used}",
            f"ticks_elapsed = {self.ticks_elapsed}",
        )

    def enforce_max_fall_speed(self):
        if self.v > 0 and abs(self.v) > self.fall_speed:
            self.v = self.fall_speed

    def allow_fastfall(self):
        input = self.input
        if input.is_down(input.DOWN) and self.v > 0:
            self.fastfall = True
            self.v = self.fall_speed

    def allow_aerial_drift(self):
        input = self.input
        # update horizontal position
        if input.is_down(input.LEFT):
            self.u -= self.air_acceleration
        if input.is_down(input.RIGHT):
            self.u += self.air_acceleration
        # limit horizontal speed
        if abs(self.u) > self.air_speed:
            self.u = sign(self.u) * self.air_speed

    def enforce_screen_limits(self, screen_width, screen_height):
        if self.x < 0:
            self.x = 0
            self.u = 0
        if self.x > screen_width:
            self.x = screen_width
            self.u = 0
        if self.y < 0:
            self.y = 0
            self.v = 0
        if self.y > screen_height:
            self.y = screen_height
            self.v = 0

    # ========================= state functions ================================

    def state_stand(self):
        self.image = self.sprites["stand_" + self.facing].get_frame(self.frames_elapsed)
        input = self.input
        if input.is_pressed(input.Y):
            self.state = self.state_jumpsquat
        if input.is_down(input.DOWN):
            self.state = self.state_squat
        if input.is_down(input.LEFT) or input.is_down(input.RIGHT):
            self.state = self.state_run
        if input.is_down(input.A):
            self.state = self.StandingDefense(self)
        if input.is_down(input.B):
            self.state = self.WeirdHit(self)
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.state_fall

    def state_jumpsquat(self):
        self.image = self.sprites["crouch_" + self.facing].get_frame(self.frames_elapsed)

        if self.ticks_elapsed == self.jumpsquat_frames:
            # if still holding jump, do a fullhop
            if self.input.is_down(self.input.Y):
                self.enter_jump()
            # else do a shorthop
            else:
                self.enter_shorthop()

    def state_divesquat(self):
        self.image = self.sprites["crouch_" + self.facing].get_frame(self.frames_elapsed)

        if self.ticks_elapsed == self.jumpsquat_frames:
            self.enter_dive()

    def enter_dive(self):
        self.u = 40 if self.facing_right else -40
        self.v = -self.jump_power / 3
        self.y -= 1
        self.state = self.Dive(self)
        self.fastfall = False

    def enter_jump(self):
        self.v = -self.jump_power
        self.y -= 1  # need this to become airborne. Hacky?
        self.state = self.state_fall
        self.fastfall = False

    def enter_shorthop(self):
        self.v = -self.shorthop_power
        self.y -= 1  # need this to become airborne. Hacky?
        self.state = self.state_fall
        self.fastfall = False

    def state_fall(self):
        self.image = self.sprites["jump_" + self.facing].get_frame(self.frames_elapsed)
        input = self.input

        holding_back = (self.facing_right and input.is_down(input.LEFT)) or (
            not self.facing_right and input.is_down(input.RIGHT)
        )
        holding_forward = (self.facing_right and input.is_down(input.RIGHT)) or (
            not self.facing_right and input.is_down(input.LEFT)
        )
        Cstick_back = (self.facing_right and input.is_pressed(input.C_LEFT)) or (
            not self.facing_right and input.is_pressed(input.C_RIGHT)
        )
        Cstick_forward = (self.facing_right and input.is_pressed(input.C_RIGHT)) or (
            not self.facing_right and input.is_pressed(input.C_LEFT)
        )

        # aerial hits
        if input.is_down(input.A):
            self.state = self.AerialDefense(self)

        if (input.is_pressed(input.B) and holding_back) or Cstick_back:
            self.state = self.BackAir(self)

        if (input.is_pressed(input.B) and (holding_forward or not holding_back)) or Cstick_forward:
            self.state = self.ForwardAir(self)

        if input.is_pressed(input.C_DOWN):
            self.state = self.DownAir(self)

        # double-jump
        if (
            input.is_pressed(input.Y)
            and self.aerial_jumps_used < self.aerial_jumps
            and not self.double_jump_cooldown
        ):
            self.double_jump_cooldown = self.double_jump_cooldown_frames
            self.aerial_jumps_used += 1
            self.enter_jump()

        self.enforce_max_fall_speed()
        self.allow_fastfall()
        self.allow_aerial_drift()

        if not self.airborne:
            self.state = self.state_stand
            self.v = 0

    class Dive(VolleyballMove):
        sprite_animation_name = "dive"
        left_and_right_versions = True

        def __init__(self, instance):
            self.sweet_spot = Hitbox(
                owner=instance,
                knockback=20,
                knockback_angle=95,
                angle=0,
                x_offset=30,
                y_offset=-45,
                width=50,
                height=20,
            )
            self.hitbox_mapping = {
                (0, 999): [self.sweet_spot],
            }
            super().__init__(instance)

        def __call__(self):
            super().__call__()
            instance = self.instance
            input = instance.input
            # update horizontal position
            if input.is_down(input.LEFT):
                instance.u -= instance.air_acceleration
            if input.is_down(input.RIGHT):
                instance.u += instance.air_acceleration
            # limit dive speed
            if abs(instance.u) > instance.dive_speed:
                instance.u = sign(instance.u) * instance.dive_speed

            instance.enforce_max_fall_speed()
            instance.allow_fastfall()

            if not instance.airborne:
                instance.state = instance.state_dive_getup
                instance.v = 0

    def state_dive_getup(self):
        animation = self.sprites["dive_getup_" + self.facing]
        image = animation.get_frame(self.frames_elapsed)
        if image:
            self.image = image
        else:
            self.state = self.state_stand

    class StandingDefense(VolleyballMove):
        sprite_animation_name = "standing_hit"
        left_and_right_versions = True

        def __init__(self, instance):
            self.sweet_spot = Hitbox(
                owner=instance,
                knockback=20,
                knockback_angle=70,
                angle=0,
                x_offset=15,
                y_offset=-45,
                width=50,
                height=20,
            )
            self.sour_spot = Hitbox(
                owner=instance,
                knockback=10,
                knockback_angle=91,
                angle=0,
                x_offset=20,
                y_offset=-45,
                width=30,
                height=10,
            )
            # todo: if key is None the hitbox should map to ALL frames.
            self.hitbox_mapping = {
                (0, 1): [self.sweet_spot],
                (2, 999): [self.sour_spot],
            }
            super().__init__(instance)

        def __call__(self):
            super().__call__()
            instance = self.instance
            input = instance.input
            if not input.is_down(input.A):
                instance.state = instance.state_stand

    class WeirdHit(VolleyballMove):
        sprite_animation_name = "weird_hit"
        left_and_right_versions = True

        def __init__(self, instance):
            self.first_hitbox = Hitbox(
                owner=instance,
                knockback=20,
                angle=10,
                knockback_angle=80,
                x_offset=15,
                y_offset=-55,
                width=40,
                height=20,
            )
            self.second_hitbox = Hitbox(
                owner=instance,
                knockback=20,
                angle=-10,
                knockback_angle=120,
                x_offset=5,
                y_offset=-90,
                width=50,
                height=30,
            )
            self.third_hitbox = Hitbox(
                owner=instance,
                knockback=20,
                angle=10,
                knockback_angle=180,
                x_offset=-15,
                y_offset=-90,
                width=50,
                height=30,
            )
            self.hitbox_mapping = {
                (1, 2): [self.first_hitbox],
                (2, 3): [self.second_hitbox],
                (3, 6): [self.third_hitbox],
            }
            super().__init__(instance)

        def __call__(self):
            super().__call__()
            self.end_when_animation_ends(self.instance.state_stand)

    class AerialDefense(VolleyballMove):
        sprite_animation_name = "aerial_defense"
        left_and_right_versions = True

        def __init__(self, instance):
            self.sweet_spot = Hitbox(
                owner=instance,
                knockback=20,
                knockback_angle=70,
                angle=0,
                x_offset=0,
                y_offset=-90,
                width=50,
                height=20,
            )
            self.sour_spot = Hitbox(
                owner=instance,
                knockback=10,
                knockback_angle=91,
                angle=0,
                x_offset=0,
                y_offset=-90,
                width=30,
                height=10,
            )
            self.hitbox_mapping = {
                (0, 1): [self.sweet_spot],
                (2, 999): [self.sour_spot],
            }
            super().__init__(instance)

        def __call__(self):
            instance = self.instance
            input = instance.input
            super().__call__()
            instance.enforce_max_fall_speed()
            instance.allow_fastfall()
            instance.allow_aerial_drift()
            if not input.is_down(input.A):
                instance.state = instance.state_fall
            if not instance.airborne:
                instance.state = instance.state_stand

    class ForwardAir(VolleyballMove):
        sprite_animation_name = "flying_kick"
        left_and_right_versions = True

        def __init__(self, instance):
            self.back_knee = Hitbox(
                owner=instance,
                knockback=7,
                knockback_angle=100,
                angle=30,
                x_offset=-20,
                y_offset=-30,
                width=40,
                height=30,
            )
            self.sweet_spot = Hitbox(
                owner=instance,
                knockback=20,
                knockback_angle=10,
                angle=0,
                x_offset=20,
                y_offset=-40,
                width=60,
                height=20,
            )
            self.sour_spot = Hitbox(
                owner=instance,
                knockback=10,
                knockback_angle=45,
                angle=0,
                x_offset=25,
                y_offset=-40,
                width=30,
                height=10,
            )
            self.hitbox_mapping = {
                (1, 1): [self.sweet_spot, self.back_knee],
                (2, 5): [self.sour_spot, self.back_knee],
            }
            super().__init__(instance)

        def __call__(self):
            super().__call__()
            instance = self.instance
            instance.enforce_max_fall_speed()
            instance.allow_fastfall()
            instance.allow_aerial_drift()
            self.end_when_animation_ends(instance.state_fall)
            if not instance.airborne:
                instance.state = instance.state_stand

    class BackScoop(VolleyballMove):
        sprite_animation_name = "back_air"
        left_and_right_versions = True

        def __init__(self, instance):
            self.sweet_spot = Hitbox(
                owner=instance,
                knockback=20,
                angle=-30,
                knockback_angle=120,
                x_offset=20,
                y_offset=-80,
                width=30,
                height=50,
            )
            self.sour_spot = Hitbox(
                owner=instance,
                knockback=10,
                angle=-30,
                knockback_angle=120,
                x_offset=20,
                y_offset=-80,
                width=25,
                height=45,
            )
            self.hitbox_mapping = {
                (1, 2): [self.sweet_spot],
                (3, 99): [self.sour_spot],
            }
            super().__init__(instance)

        def __call__(self):
            super().__call__()
            instance = self.instance
            instance.enforce_max_fall_speed()
            instance.allow_fastfall()
            instance.allow_aerial_drift()
            self.end_when_animation_ends(instance.state_fall)
            if not instance.airborne:
                instance.state = instance.state_stand

    class BackAir(VolleyballMove):
        sprite_animation_name = "back_air2"
        left_and_right_versions = True

        def __init__(self, instance):
            self.sweet_spot = Hitbox(
                owner=instance,
                knockback=20,
                angle=-30,
                knockback_angle=170,
                x_offset=-35,
                y_offset=-55,
                width=30,
                height=30,
            )
            self.sour_spot = Hitbox(
                owner=instance,
                knockback=10,
                angle=30,
                knockback_angle=120,
                x_offset=-20,
                y_offset=-80,
                width=40,
                height=20,
            )
            self.hitbox_mapping = {
                (2, 4): [self.sweet_spot, self.sour_spot],
            }
            super().__init__(instance)

        def __call__(self):
            super().__call__()
            instance = self.instance
            instance.enforce_max_fall_speed()
            instance.allow_fastfall()
            instance.allow_aerial_drift()
            self.end_when_animation_ends(instance.state_fall)
            if not instance.airborne:
                instance.state = instance.state_stand

    class DownAir(VolleyballMove):
        sprite_animation_name = "stomp"
        left_and_right_versions = True

        def __init__(self, instance):
            self.nipple_spike = Hitbox(
                owner=instance,
                knockback=20,
                angle=0,
                knockback_angle=280,
                x_offset=0,
                y_offset=-70,
                width=60,
                height=30,
            )
            self.feet = Hitbox(
                owner=instance,
                knockback=25,
                angle=0,
                knockback_angle=270,
                x_offset=5,
                y_offset=-20,
                width=30,
                height=60,
            )
            self.hitbox_mapping = {
                (3, 5): [self.feet, self.nipple_spike],
            }
            super().__init__(instance)

        def __call__(self):
            super().__call__()
            instance = self.instance
            instance.enforce_max_fall_speed()
            instance.allow_fastfall()
            instance.allow_aerial_drift()
            self.end_when_animation_ends(instance.state_fall)
            if not instance.airborne:
                instance.state = instance.state_stand

    class Taunt(VolleyballMove):
        left_and_right_versions = True
        sprite_animation_name = "taunt"

        def __init__(self, instance):
            self.hitbox = Hitbox(
                owner=instance,
                knockback=25,
                angle=10,
                knockback_angle=50,
                x_offset=0,
                y_offset=-60,
                width=90,
                height=60,
            )
            self.hitbox2 = Hitbox(
                owner=instance,
                knockback=15,
                angle=-30,
                knockback_angle=90,
                x_offset=0,
                y_offset=-35,
                width=90,
                height=60,
            )
            self.hitbox_mapping = {
                (3, 9): [self.hitbox],
                (10, 999): [self.hitbox2],
            }
            super().__init__(instance)

        def __call__(self):
            super().__call__()

            if not self.image:
                self.instance.image = self.sprite_animation.frames[-1]

            if self.instance.frames_elapsed == 30:
                self.instance.state = self.instance.state_stand

    def state_squat(self):
        self.image = self.sprites["crouch_" + self.facing].get_frame(self.frames_elapsed)
        input = self.input
        if self.airborne:
            self.state = self.state_fall
        if input.is_pressed(input.Y):
            self.state = self.state_jumpsquat
        if not input.is_down(input.DOWN):
            self.state = self.state_stand
        if self.frames_elapsed == 3:
            self.state = self.Taunt(self)

    def state_run(self):
        self.image = self.sprites["run_" + self.facing].get_frame(self.frames_elapsed)
        input = self.input
        if not input.is_down(input.LEFT) and not input.is_down(input.RIGHT):
            self.state = self.state_stand
        if input.is_down(input.LEFT):
            self.facing_right = False
            self.u -= self.ground_acceleration
        if input.is_down(input.RIGHT):
            self.facing_right = True
            self.u += self.ground_acceleration
        if abs(self.u) > self.ground_speed:  # enforce run speed
            self.u = sign(self.u) * self.ground_speed
        if input.is_pressed(input.Y):
            self.state = self.state_jumpsquat
        if input.is_down(input.DOWN):
            self.state = self.state_squat
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.state_fall
        if input.is_pressed(input.A):
            if abs(self.u) == self.ground_speed:
                self.state = self.state_divesquat
            else:
                self.state = self.StandingDefense(self)

    def handle_hit(self, hitbox):
        self.level.add(ParticleEffect(*hitbox.rect.center), type="particle_effect")


class SingleUseAnimation(Entity, AnimationMixin):
    width: int
    height: int
    sprite_animation: SpriteAnimation
    game_ticks_per_sprite_frame = conf.TICKS_PER_SPRITE_FRAME

    def __init__(self, x, y):
        super().__init__(x, y, self.width, self.height)

    def update(self):
        self.update_animation()
        # todo: why doesn't update_animation do this?
        self.image = self.sprite_animation.get_frame(self.frames_elapsed)
        if not self.sprite_animation.get_frame(self.frames_elapsed + 1):
            self.kill()


class ParticleEffect(SingleUseAnimation):
    width = 100
    height = 100

    def __init__(self, x, y):
        super().__init__(x, y)
        self.sprites = explosion_sprites()
        self.sprite_animation = self.sprites["default"]
        self.image = self.sprite_animation.get_frame(0)


class Stickman(Player):
    mass = 1
    width = 80
    height = 70
    _state = None
    ground_acceleration = 10  # 3
    ground_speed = 9
    air_acceleration = 2
    air_speed = ground_speed
    dive_speed = 10
    gravity = 1.5
    _fall_speed = 5
    fastfall_multiplier = 3
    aerial_jumps = 1
    jump_power = 20
    shorthop_power = 11
    jumpsquat_frames = 3
    friction = 0.8
    air_resistance = 0.03
    crouch_height_multiplier = 0.7

    # cooldowns -- todo: put this in a mixin?
    double_jump_cooldown_frames = 15  # should this go in the Character class?
    double_jump_cooldown = 0
    projectile_cooldown_frames = 30
    projectile_cooldown = 0

    sprites_folder = Path("sprites/")
    image = pygame.image.load((sprites_folder / "stickman/stick_stand.png").as_posix())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sprites = stickman_sprites()


class Ball(Entity, AnimationMixin, PhysicsMixin):
    width: int
    height: int
    mass: int
    bounciness: float  # max 1: 100% efficient bounce
    gravity: float
    air_resistance: float
    last_touched_by: Player = None

    def __init__(self, x, y, groups=[]):
        super().__init__(x, y, self.width, self.height, groups=groups)
        self.sprites = volleyball_sprites()
        self.image = self.sprites["default"].get_frame(0)

    def update(self):
        # todo: idea: what if I put update_physics etc in states. That way each state could
        #  decide how to do physics. This would make the state machine pattern a lot more
        #  general, and would allow "non-physical" states like "handheld" (following a player;
        #  physics off) and "airborne" (physics on).
        #  The same goes for handling hits. States could allow or not allow self to be hit.
        self.handle_collisions()
        self.update_physics()
        self.update_animation()
        self.enforce_screen_limits(*self.level.game.screen_size)

    def update_physics(self):
        # update vertical position
        self.v += self.gravity

        # todo: really i should subtract the air resistance from the resultant vector, but whatever
        self.u *= 1 - self.air_resistance
        self.v *= 1 - self.air_resistance

        # update position
        self.x += self.u
        self.y += self.v

        # don't allow sub-pixel speeds
        self.u = 0 if abs(self.u) < 0.5 else self.u

    def handle_collision_with_player(self, player):
        print(f"collided with {player}")
        # calculate the normal vector of the collision "plane" and normalize it
        delta_x = self.centroid.x - player.centroid.x
        delta_y = self.centroid.y - player.centroid.y
        normal_vector = numpy.array([delta_x, delta_y])
        normal_vector_magnitude = numpy.linalg.norm(normal_vector)
        normal_vector_normalized = normal_vector / normal_vector_magnitude
        # calculate the ball's incident velocity vector
        incident = numpy.array([self.u, self.v])
        # calculate the resultant velocity vector
        resultant = (
            incident - 2 * numpy.dot(incident, normal_vector_normalized) * normal_vector_normalized
        )
        self.velocity = resultant + player.velocity

        # prevent overlapping
        un_overlap(movable_object=self, immovable_object=player)

    def handle_collision_with_platform(self, platform):
        print(f"collided with {platform}")
        # calculate the normal vector of the collision plane and normalize it
        x_overlap, y_overlap = get_overlap_between_objects(self, platform)
        if x_overlap > y_overlap:
            # bounce vertically
            if self.centroid.y <= platform.centroid.y:
                normal_vector = numpy.array([0, 1])
            else:
                normal_vector = numpy.array([0, -1])

        else:  # y_overlap > 2 * x_overlap:
            # bounce horizontally
            if self.centroid.x <= platform.centroid.x:
                normal_vector = numpy.array([-1, 0])
            else:
                normal_vector = numpy.array([1, 0])

        normal_vector_magnitude = numpy.linalg.norm(normal_vector)
        normal_vector_normalized = normal_vector / normal_vector_magnitude
        # calculate the ball's incident velocity vector
        incident = numpy.array([self.u, self.v])
        # calculate the resultant velocity vector
        resultant = (
            incident - 2 * numpy.dot(incident, normal_vector_normalized) * normal_vector_normalized
        )
        self.velocity = resultant

        # prevent overlapping
        un_overlap(movable_object=self, immovable_object=platform)

    def handle_collisions(self):
        platforms = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
        for platform in platforms:
            self.handle_collision_with_platform(platform)

    def handle_hit(self, hitbox):
        self.last_touched_by = hitbox.owner
        self.level.add(ParticleEffect(self.x, self.y), type="particle_effect")
        print(f"Ball hit by hitbox {id(hitbox)}")

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


class Volleyball(Ball):
    mass = 1
    width = 40
    height = 40
    bounciness = 1
    gravity = 0.5
    air_resistance = 0.01


class Bowlingball(Ball):
    mass = 4
    width = 30
    height = 30
    bounciness = 0.5
    gravity = 0.5
    air_resistance = 0.01


class HitHandler:
    def __init__(self):
        # queue for storing
        self.queue = deque(maxlen=200)

    def handle_hits(self, hitboxes, objects):
        """
        Manage the effects of hitboxes hitting other entities.

        This function shouldn't know the details of how each object reacts to getting hit. That
        is the responsibility of the object to define those methods. This function's
        responsibility is to ensure no object instance is hit more than once by the same hitbox
        instance.
        """

        for object in objects:
            colliding_hitboxes = pygame.sprite.spritecollide(object, hitboxes, dokill=False)
            for hitbox in colliding_hitboxes:
                # hitboxes should never hit their owner
                if hitbox.owner == object:
                    continue

                # if these two instances have already met, don't repeat the interaction
                if (hitbox, object) in self.queue:
                    continue

                self.handle_hitbox_collision(hitbox, object)
                self.add_completed_pair(hitbox, object)

        # todo: prevent duplicates
        #  in order to do this, this function needs to maintain state. How?

    @staticmethod
    def handle_hitbox_collision(hitbox, object):
        # todo: apply hitbox damage?
        # here's where we calculate how far/fast the object gets knocked
        magnitude = hitbox.knockback / object.mass
        u = magnitude * numpy.cos(numpy.deg2rad(hitbox.knockback_angle))
        v = -magnitude * numpy.sin(numpy.deg2rad(hitbox.knockback_angle))
        object.u = u
        object.v = v
        object.x += u
        object.y += v
        object.handle_hit(hitbox)
        hitbox.handle_hit(object)

    def add_completed_pair(self, hitbox, object):
        self.queue.append((hitbox, object))


class PersistentHitbox(ParticleEffect):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hitbox = Hitbox(
            knockback_angle=90, knockback=5, width=200, height=200, angle=0, x=x, y=y, owner=self
        )

    def update(self):
        super().update()
        self.level.add_hitbox(self.hitbox)
