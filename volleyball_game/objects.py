from pathlib import Path

import numpy
import pygame as pygame
from numpy.core._multiarray_umath import sign

from base.animation import SpriteDict
from base.keyhandler import KeyHandler
from base.objects.entities import Entity, CollisionMixin, Point
from base.objects.mixins import HistoryMixin, AnimationMixin, PhysicsMixin
from base.utils import get_overlap_between_objects, un_overlap
from volleyball_game.sprites.stickman import stickman_sprites
from volleyball_game.sprites.volleyball import volleyball_sprites


# todo: allow states to describe the rect dimensions when the entity is in that state. E.g.
#  during a dive the player's rect should be longer and thinner.


class Player(Entity, AnimationMixin, CollisionMixin, HistoryMixin):

    # class properties
    facing_right: bool
    width: int
    height: int
    _state: str
    ground_acceleration: float
    ground_speed: float
    air_acceleration: float
    air_speed: float
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

    # cooldowns -- todo: put this in a mixin?
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

    # references to other objects
    level = None

    # historymixin
    attributes_to_remember = ["rect", "x", "y"]

    def __init__(self, x, y, facing_right=True, keymap=None, groups=[]):

        super().__init__(x, y, self.width, self.height, groups=groups)
        HistoryMixin.__init__(self)

        self.u = 0
        self.v = 0
        self.state = self.states.FALL
        self.fastfall = False
        self.facing_right = facing_right
        self.keymap = keymap
        self.state_lookup = {
            self.states.STAND: self.state_stand,
            self.states.JUMPSQUAT: self.state_jumpsquat,
            self.states.FALL: self.state_fall,
            self.states.RUN: self.state_run,
            self.states.SQUAT: self.state_squat,
            self.states.DIVE: self.state_dive,
            self.states.DIVESQUAT: self.state_divesquat,
            self.states.DIVE_GETUP: self.state_dive_getup,
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
    def base(self):
        # todo: do we even need this anymore?
        return Point(*self.rect.midbottom)

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
            f"frames_elapsed = {self.frames_elapsed}",
        )

    def enforce_max_fall_speed(self):
        if self.v > 0 and abs(self.v) > self.fall_speed:
            self.v = self.fall_speed

    def allow_fastfall(self):
        if KeyHandler.is_pressed(self.keymap.DOWN) and self.v > 0:
            self.fastfall = True
            self.v = self.fall_speed

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

        if KeyHandler.is_pressed(self.keymap.UP):  # enter jumpsquat
            self.state = self.states.JUMPSQUAT
        if KeyHandler.is_down(self.keymap.DOWN):  # enter squat
            self.state = self.states.SQUAT
        if KeyHandler.is_down(self.keymap.LEFT) or KeyHandler.is_down(self.keymap.RIGHT):
            self.state = self.states.RUN
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.states.FALL

    def state_jumpsquat(self):
        self.image = self.sprites["crouch_" + self.facing].get_frame(self.frames_elapsed)

        if self.frames_elapsed == self.jumpsquat_frames:
            self.enter_jump()

    def state_divesquat(self):
        self.image = self.sprites["crouch_" + self.facing].get_frame(self.frames_elapsed)

        if self.frames_elapsed == self.jumpsquat_frames:
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

        # update horizontal position
        if KeyHandler.is_down(self.keymap.LEFT):
            self.u -= self.air_acceleration
        if KeyHandler.is_down(self.keymap.RIGHT):
            self.u += self.air_acceleration
        # limit horizontal speed
        if abs(self.u) > self.air_speed:
            self.u = sign(self.u) * self.air_speed

        # double-jump
        if (
            KeyHandler.is_pressed(self.keymap.UP)
            and self.aerial_jumps_used < self.aerial_jumps
            and not self.double_jump_cooldown
        ):
            self.double_jump_cooldown = self.double_jump_cooldown_frames
            self.aerial_jumps_used += 1
            self.enter_jump()

        self.enforce_max_fall_speed()
        self.allow_fastfall()

        if not self.airborne:
            self.state = self.states.STAND
            self.v = 0

    def state_dive(self):
        self.image = self.sprites["dive_" + self.facing].get_frame(self.frames_elapsed)

        # update horizontal position
        if KeyHandler.is_down(self.keymap.LEFT):
            self.u -= self.air_acceleration
        if KeyHandler.is_down(self.keymap.RIGHT):
            self.u += self.air_acceleration
        # limit dive speed
        if abs(self.u) > self.dive_speed:
            self.u = sign(self.u) * self.dive_speed

        self.enforce_max_fall_speed()
        self.allow_fastfall()

        if not self.airborne:
            self.state = self.states.DIVE_GETUP
            self.v = 0

    def state_dive_getup(self):
        self.rect
        animation = self.sprites["dive_getup_" + self.facing]
        image = animation.get_frame(self.frames_elapsed)
        if image:
            self.image = image
        else:
            self.state = self.states.STAND

    def state_squat(self):
        self.image = self.sprites["crouch_" + self.facing].get_frame(self.frames_elapsed)

        if self.airborne:
            self.state = self.states.FALL
        if KeyHandler.is_pressed(self.keymap.UP):
            self.state = self.states.JUMPSQUAT
        # if squat key released, exit squat state
        if not KeyHandler.is_down(self.keymap.DOWN):
            self.state = self.states.STAND

    def state_run(self):
        self.image = self.sprites["run_" + self.facing].get_frame(self.frames_elapsed)

        if not KeyHandler.is_down(self.keymap.LEFT) and not KeyHandler.is_down(self.keymap.RIGHT):
            self.state = self.states.STAND
        if KeyHandler.is_down(self.keymap.LEFT):
            self.facing_right = False
            self.u -= self.ground_acceleration
        if KeyHandler.is_down(self.keymap.RIGHT):
            self.facing_right = True
            self.u += self.ground_acceleration
        if abs(self.u) > self.ground_speed:  # enforce run speed
            self.u = sign(self.u) * self.ground_speed
        if KeyHandler.is_pressed(self.keymap.UP):
            self.state = self.states.JUMPSQUAT
        if KeyHandler.is_down(self.keymap.DOWN):
            self.state = self.states.SQUAT
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.states.FALL
        if KeyHandler.is_down(self.keymap.A) and abs(self.u) == self.ground_speed:
            self.state = self.states.DIVESQUAT


class Stickman(Player):
    width = 80
    height = 70
    _state = None
    ground_acceleration = 1
    ground_speed = 7
    air_acceleration = 0.5
    air_speed = ground_speed
    dive_speed = 10
    gravity = 1.2
    _fall_speed = 5
    fastfall_multiplier = 2.5
    aerial_jumps = 1
    jump_power = 15
    jumpsquat_frames = 6
    friction = 0.3
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

    # def handle_hits(self):
    #     hitboxes = pygame.sprite.spritecollide(
    #         self, self.level.hitboxes, collided=pygame.sprite.collide_mask, dokill=False
    #     )
    #     for hitbox in hitboxes:
    #         print(f"Ball hit by {hitbox.owner}'s hitbox")
    #         # self.kill()
    #         self.u = 10
    #         self.v = -100

    def handle_collision_with_player(self, player):
        # bounce self away from collided object
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
            incident
            - 2 * numpy.dot(incident, normal_vector_normalized) * normal_vector_normalized
        )
        self.u, self.v = resultant + player.velocity

        # prevent overlapping
        un_overlap(movable_object=self, immovable_object=player)

    def handle_collision_with_platform(self, platform):
        # bounce self away from collided object
        print(f"collided with {platform}")
        # calculate the normal vector of the collision plane and normalize it
        ## get the overlapping pixels
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
            incident
            - 2 * numpy.dot(incident, normal_vector_normalized) * normal_vector_normalized
        )
        self.u, self.v = resultant

        # prevent overlapping
        un_overlap(movable_object=self, immovable_object=platform)

    def handle_collisions(self):
        players = pygame.sprite.spritecollide(self, self.level.characters, dokill=False)
        for player in players:
            self.handle_collision_with_player(player)

        platforms = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
        for platform in platforms:
            self.handle_collision_with_platform(platform)

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
    width = 50
    height = 50
    bounciness = 1
    gravity = 0.5
    air_resistance = 0.01
