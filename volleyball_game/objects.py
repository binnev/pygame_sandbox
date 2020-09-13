from pathlib import Path

import numpy
import pygame as pygame
from numpy.core._multiarray_umath import sign

from base.animation import SpriteDict, SpriteAnimation
from base.objects.entities import Entity, CollisionMixin, Move, Hitbox
from base.objects.mixins import HistoryMixin, AnimationMixin, PhysicsMixin
from base.utils import get_overlap_between_objects, un_overlap
from volleyball_game import conf
from volleyball_game.sprites.particle_effects import explosion_sprites
from volleyball_game.sprites.stickman import stickman_sprites
from volleyball_game.sprites.volleyball import volleyball_sprites


# todo: allow states to describe the rect dimensions when the entity is in that state. E.g.
#  during a dive the player's rect should be longer and thinner.
class VolleyballMove(Move):
    sprite_animation_name: str
    left_and_right_versions: bool
    hitboxes: ["Hitbox"]
    active_hitboxes: ["Hitbox"]

    def __call__(self):
        """ This is the equivalent to the function states """
        # fixme: convert to frames
        # flip sprite animation automatically
        name = self.sprite_animation_name
        if self.left_and_right_versions:
            name += "_" + self.instance.facing
        self.sprite_animation = self.instance.sprites[name]

        super().__call__(self.instance.frames_elapsed)

        self.instance.image = self.image

        # flip hitboxes
        if not self.instance.facing_right:
            self.active_hitboxes = self.flip_hitboxes(self.active_hitboxes)

        for hitbox in self.active_hitboxes:
            self.instance.level.add_hitbox(hitbox)

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
    jumpsquat_frames: int
    friction: float
    air_resistance: float
    crouch_height_multiplier: float

    # drawing
    sprites: SpriteDict
    image: pygame.Surface

    double_jump_cooldown_frames = 15
    double_jump_cooldown = 0

    class states:
        DEFAULT = "DEFAULT"
        JUMPSQUAT = "JUMPSQUAT"
        JUMP = "JUMP"
        STAND = "STAND"
        RUN = "RUN"
        SQUAT = "SQUAT"
        FALL = "FALL"
        DIVE = "DIVE"
        DIVESQUAT = "DIVESQUAT"
        DIVE_GETUP = "DIVE_GETUP"
        STANDING_DEFENSE = "STANDING_DEFENSE"
        AERIAL_DEFENSE = "AERIAL_DEFENSE"
        AERIAL_ATTACK = "AERIAL_ATTACK"
        BACK_AIR = "BACK_AIR"
        WEIRD_HIT = "WEIRD_HIT"
        TAUNT = "TAUNT"

    # references to other objects
    level = None

    # historymixin
    attributes_to_remember = ["rect", "x", "y"]

    def __init__(self, x, y, facing_right=True, input=None, groups=[]):

        super().__init__(x, y, self.width, self.height, groups=groups)
        HistoryMixin.__init__(self)

        self.u = 0
        self.v = 0
        self.state = self.states.FALL
        self.fastfall = False
        self.facing_right = facing_right
        self.input = input
        self.state_lookup = {
            self.states.STAND: self.state_stand,
            self.states.JUMPSQUAT: self.state_jumpsquat,
            self.states.FALL: self.state_fall,
            self.states.RUN: self.state_run,
            self.states.SQUAT: self.state_squat,
            self.states.DIVE: self.Dive(self),
            self.states.DIVESQUAT: self.state_divesquat,
            self.states.DIVE_GETUP: self.state_dive_getup,
            self.states.STANDING_DEFENSE: self.StandingDefense(self),
            self.states.AERIAL_DEFENSE: self.AerialDefense(self),
            self.states.AERIAL_ATTACK: self.AerialAttack(self),
            self.states.BACK_AIR: self.BackAir(self),
            self.states.WEIRD_HIT: self.WeirdHit(self),
            self.states.TAUNT: self.Taunt(self),
        }
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
        if self.state in [self.states.SQUAT, self.states.JUMPSQUAT]:
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
        self.execute_state()
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

    def execute_state(self):
        """Each state has a corresponding function that handles keypresses and events"""
        func = self.state_lookup[self.state]  # grab the state function
        func()  # execute it

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
            self.state = self.states.JUMPSQUAT
        if input.is_down(input.DOWN):
            self.state = self.states.SQUAT
        if input.is_down(input.LEFT) or input.is_down(input.RIGHT):
            self.state = self.states.RUN
        if input.is_down(input.A):
            self.state = self.states.STANDING_DEFENSE
        if input.is_down(input.B):
            self.state = self.states.WEIRD_HIT
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.states.FALL

    def state_jumpsquat(self):
        self.image = self.sprites["crouch_" + self.facing].get_frame(self.frames_elapsed)

        if self.ticks_elapsed == self.jumpsquat_frames:
            self.enter_jump()

    def state_divesquat(self):
        self.image = self.sprites["crouch_" + self.facing].get_frame(self.frames_elapsed)

        if self.ticks_elapsed == self.jumpsquat_frames:
            self.enter_dive()

    def enter_dive(self):
        self.u = 40 if self.facing_right else -40
        self.v = -self.jump_power / 3
        self.y -= 1
        self.state = self.states.DIVE
        self.fastfall = False

    def enter_jump(self):
        self.v = -self.jump_power
        self.y -= 1  # need this to become airborne. Hacky?
        self.state = self.states.FALL
        self.fastfall = False

    def state_fall(self):
        self.image = self.sprites["jump_" + self.facing].get_frame(self.frames_elapsed)
        input = self.input
        # aerial hits
        if input.is_down(input.A):
            self.state = self.states.AERIAL_DEFENSE
        if input.is_down(input.B):
            # if holding back -> "back air"
            if (self.facing_right and input.is_down(input.LEFT)) or (
                not self.facing_right and input.is_down(input.RIGHT)
            ):
                self.state = self.states.BACK_AIR
            else:
                # if holding forward or no direction input -> "forward air"
                self.state = self.states.AERIAL_ATTACK

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
            self.state = self.states.STAND
            self.v = 0

    class Dive(VolleyballMove):
        sweet_spot = dict(
            knockback=20,
            knockback_angle=95,
            angle=0,
            x_offset=30,
            y_offset=-45,
            width=50,
            height=20,
        )
        hitbox_mapping = {
            (0, 999): [sweet_spot],
        }
        sprite_animation_name = "dive"
        left_and_right_versions = True

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
                instance.state = instance.states.DIVE_GETUP
                instance.v = 0

    def state_dive_getup(self):
        animation = self.sprites["dive_getup_" + self.facing]
        image = animation.get_frame(self.frames_elapsed)
        if image:
            self.image = image
        else:
            self.state = self.states.STAND

    class StandingDefense(VolleyballMove):
        sweet_spot = dict(
            knockback=20,
            knockback_angle=70,
            angle=0,
            x_offset=15,
            y_offset=-45,
            width=50,
            height=20,
        )
        sour_spot = dict(
            knockback=10,
            knockback_angle=91,
            angle=0,
            x_offset=20,
            y_offset=-45,
            width=30,
            height=10,
        )
        # todo: if key is None the hitbox should map to ALL frames.
        hitbox_mapping = {
            (0, 1): [sweet_spot],
            (2, 999): [sour_spot],
        }
        sprite_animation_name = "standing_hit"
        left_and_right_versions = True

        def __call__(self):
            super().__call__()
            instance = self.instance
            input = instance.input
            if not input.is_down(input.A):
                instance.state = instance.states.STAND

    class WeirdHit(VolleyballMove):
        first_hitbox = dict(
            knockback=20,
            angle=10,
            knockback_angle=80,
            x_offset=15,
            y_offset=-55,
            width=40,
            height=20,
        )
        second_hitbox = dict(
            knockback=20,
            angle=-10,
            knockback_angle=120,
            x_offset=5,
            y_offset=-90,
            width=50,
            height=30,
        )
        third_hitbox = dict(
            knockback=20,
            angle=10,
            knockback_angle=180,
            x_offset=-15,
            y_offset=-90,
            width=50,
            height=30,
        )

        hitbox_mapping = {
            (1, 2): [first_hitbox],
            (2, 3): [second_hitbox],
            (3, 6): [third_hitbox],
        }
        sprite_animation_name = "weird_hit"
        left_and_right_versions = True

        def __call__(self):
            super().__call__()
            self.end_when_animation_ends(self.instance.states.STAND)

    class AerialDefense(VolleyballMove):
        sweet_spot = dict(
            knockback=20,
            knockback_angle=70,
            angle=0,
            x_offset=0,
            y_offset=-90,
            width=50,
            height=20,
        )
        sour_spot = dict(
            knockback=10,
            knockback_angle=91,
            angle=0,
            x_offset=0,
            y_offset=-90,
            width=30,
            height=10,
        )
        hitbox_mapping = {
            (0, 1): [sweet_spot],
            (2, 999): [sour_spot],
        }
        sprite_animation_name = "aerial_defense"
        left_and_right_versions = True

        def __call__(self):
            instance = self.instance
            input = instance.input
            super().__call__()
            instance.enforce_max_fall_speed()
            instance.allow_fastfall()
            instance.allow_aerial_drift()
            if not input.is_down(input.A):
                instance.state = instance.states.FALL

    class AerialAttack(VolleyballMove):
        hand_hitbox = dict(
            knockback=5,
            knockback_angle=100,
            angle=0,
            x_offset=-20,
            y_offset=-70,
            width=50,
            height=30,
        )
        back_knee = dict(
            knockback=5,
            knockback_angle=160,
            angle=30,
            x_offset=-20,
            y_offset=-30,
            width=40,
            height=30,
        )
        sweet_spot = dict(
            knockback=20,
            knockback_angle=30,
            angle=0,
            x_offset=20,
            y_offset=-40,
            width=60,
            height=20,
        )
        sour_spot = dict(
            knockback=15,
            knockback_angle=30,
            angle=0,
            x_offset=25,
            y_offset=-40,
            width=30,
            height=10,
        )
        hitbox_mapping = {
            (2, 4): [sweet_spot, back_knee],
            (5, 6): [sour_spot, back_knee],
        }
        sprite_animation_name = "flying_kick"
        left_and_right_versions = True

        def __call__(self):
            super().__call__()
            self.instance.enforce_max_fall_speed()
            self.instance.allow_fastfall()
            self.instance.allow_aerial_drift()
            self.end_when_animation_ends(self.instance.states.FALL)

    class BackAir(VolleyballMove):
        sweet_spot = dict(
            knockback=20,
            angle=-30,
            knockback_angle=120,
            x_offset=20,
            y_offset=-80,
            width=30,
            height=50,
        )
        sour_spot = dict(
            knockback=10,
            angle=-30,
            knockback_angle=120,
            x_offset=20,
            y_offset=-80,
            width=25,
            height=45,
        )

        hitbox_mapping = {
            (1, 2): [sweet_spot],
            (3, 99): [sour_spot],
        }
        sprite_animation_name = "back_air"
        left_and_right_versions = True

        def __call__(self):
            super().__call__()
            self.instance.enforce_max_fall_speed()
            self.instance.allow_fastfall()
            self.instance.allow_aerial_drift()
            self.end_when_animation_ends(self.instance.states.FALL)

    class Taunt(VolleyballMove):
        hitbox = dict(
            knockback=25,
            angle=10,
            knockback_angle=50,
            x_offset=0,
            y_offset=-60,
            width=90,
            height=60,
        )
        hitbox2 = dict(
            knockback=15,
            angle=-30,
            knockback_angle=90,
            x_offset=0,
            y_offset=-35,
            width=90,
            height=60,
        )
        hitbox_mapping = {
            (3, 9): [hitbox],
            (10, 999): [hitbox2],
        }
        left_and_right_versions = True
        sprite_animation_name = "taunt"

        def __call__(self):
            super().__call__()

            if not self.image:
                self.instance.image = self.sprite_animation.frames[-1]

            if self.instance.frames_elapsed == 30:
                self.instance.state = self.instance.states.STAND

    def state_squat(self):
        self.image = self.sprites["crouch_" + self.facing].get_frame(self.frames_elapsed)
        input = self.input
        if self.airborne:
            self.state = self.states.FALL
        if input.is_pressed(input.Y):
            self.state = self.states.JUMPSQUAT
        if not input.is_down(input.DOWN):
            self.state = self.states.STAND
        if self.frames_elapsed == 3:
            self.state = self.states.TAUNT

    def state_run(self):
        self.image = self.sprites["run_" + self.facing].get_frame(self.frames_elapsed)
        input = self.input
        if not input.is_down(input.LEFT) and not input.is_down(input.RIGHT):
            self.state = self.states.STAND
        if input.is_down(input.LEFT):
            self.facing_right = False
            self.u -= self.ground_acceleration
        if input.is_down(input.RIGHT):
            self.facing_right = True
            self.u += self.ground_acceleration
        if abs(self.u) > self.ground_speed:  # enforce run speed
            self.u = sign(self.u) * self.ground_speed
        if input.is_pressed(input.Y):  # todo: change to PRESSED
            self.state = self.states.JUMPSQUAT
        if input.is_down(input.DOWN):
            self.state = self.states.SQUAT
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.states.FALL
        if input.is_pressed(input.A):  # todo: change to PRESSED
            if abs(self.u) == self.ground_speed:
                self.state = self.states.DIVESQUAT
            else:
                self.state = self.states.STANDING_DEFENSE


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
    width = 80
    height = 70
    _state = None
    ground_acceleration = 3
    ground_speed = 9
    air_acceleration = 2
    air_speed = ground_speed
    dive_speed = 10
    gravity = 1.5
    _fall_speed = 5
    fastfall_multiplier = 3
    aerial_jumps = 1
    jump_power = 20
    jumpsquat_frames = 3
    friction = 0.5
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
        # self.handle_hits()
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
        # players = pygame.sprite.spritecollide(self, self.level.characters, dokill=False)
        # for player in players:
        #     self.handle_collision_with_player(player)

        platforms = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
        for platform in platforms:
            self.handle_collision_with_platform(platform)

        hitboxes = pygame.sprite.spritecollide(self, self.level.hitboxes, dokill=False)
        for hitbox in hitboxes:
            handle_hitbox_collision(hitbox, self)
            self.last_touched_by = hitbox.owner
            self.level.add(ParticleEffect(self.x, self.y), type="particle_effect")

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


def handle_hitbox_collision(hitbox, object):
    # todo: apply hitbox damage?
    magnitude = hitbox.knockback / object.mass
    u = magnitude * numpy.cos(numpy.deg2rad(hitbox.knockback_angle))
    v = -magnitude * numpy.sin(numpy.deg2rad(hitbox.knockback_angle))
    object.u = u
    object.v = v
