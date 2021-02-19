import random
from collections import deque

import numpy
from numpy.core._multiarray_umath import sign
from pygame import Color
from pygame.rect import Rect

from base.animation import SpriteDict
from base.utils import draw_arrow
from fighting_game import sounds
from fighting_game.conf import BOUNCE_LOSS, HITPAUSE_CONSTANT, HITSTUN_CONSTANT
from fighting_game.groups import *
from fighting_game.inputs import *
from fighting_game.sprites.stickman import stickman_sprites


class Entity(Sprite):
    level: "Level"
    image: Surface = None
    debug_color = Color("red")
    rect: Rect
    game_tick = 0  # number of game ticks elapsed in the current state
    frame_duration: int  # higher = slower animation framerate

    def update(self):
        self.update_animation()

    def draw(self, surface: Surface, debug: bool = False):
        if self.image:
            surface.blit(self.image, self.image_rect)
        if debug:
            pygame.draw.rect(surface, self.debug_color, self.rect, 1)
            pygame.draw.circle(surface, self.debug_color, self.rect.center, 2, 1)

    @property
    def image_rect(self):
        """ Default is to align the image with the center of the object """
        if self.image:
            image_rect = self.image.get_rect()
            image_rect.center = self.rect.center
            return image_rect
        else:
            return None

    @property
    def x(self):
        return self.rect.centerx

    @x.setter
    def x(self, new_value):
        new_value = round(new_value)
        self.rect.centerx = new_value

    @property
    def y(self):
        return self.rect.centery

    @y.setter
    def y(self, new_value):
        new_value = round(new_value)
        self.rect.centery = new_value

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        """ Reset animation counter when state changes """
        self._state = new_state
        self.game_tick = 0

    @property
    def animation_frame(self):
        """ Convert game ticks to animation frames. """
        return self.game_tick // self.frame_duration

    def update_animation(self):
        self.game_tick += 1


class Platform(Entity):
    color = Color("gray")

    def __init__(self, x, y, width, height, droppable=False):
        super().__init__()

        self.rect = Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.droppable = droppable
        self.color = Color("green") if droppable else self.color
        self.image = Surface((width, height))
        self.image.fill(self.color)


class BlastZone(Entity):
    debug_color = Color("blue")

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = Rect(0, 0, width, height)
        self.rect.center = (x, y)


class Character(Entity):
    mass: float  # 10 is average
    damage: int
    width: int
    height: int
    color: Color
    sprites: SpriteDict
    ground_acceleration: float
    walk_speed: float
    run_speed: float
    initial_dash_duration: int
    run_turnaround_duration: int
    air_dodge_duration: int = 30
    air_dodge_speed: float = 20
    air_acceleration: float
    air_speed: float
    jump_speed: float
    shorthop_speed: float
    gravity: float
    friction: float
    air_resistance: float
    fall_speed: float
    fast_fall_speed: float
    fast_fall: bool
    jumpsquat_frames: int

    hitstun_duration: int = 0
    hitpause_duration: int = 0

    touch_box_margin = 2
    frame_duration = 3

    AttackMove: "Move"
    ForwardAir: "Move"
    BackAir: "Move"
    UpAir: "Move"
    DownAir: "Move"
    NeutralAir: "Move"
    UpSmash: "Move"
    DownSmash: "Move"
    ForwardSmash: "Move"
    UpTilt: "Move"
    DownTilt: "Move"
    ForwardTilt: "Move"
    Jab: "Move"
    GroundedSideB: "Move"
    GroundedUpB: "Move"
    GroundedDownB: "Move"
    AerialSideB: "Move"
    AerialUpB: "Move"
    AerialDownB: "Move"

    def __init__(self, x, y, input: GamecubeController, facing_right=True):
        super().__init__()

        self.rect = Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.u = 0
        self.v = 0
        self.input = input
        self.facing_right = facing_right
        self.fast_fall = False

    def update(self):
        super().update()
        self.state()

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        if debug:
            # draw touchbox
            pygame.draw.rect(surface, Color("goldenrod"), self.touch_box, 1)

    @property
    def facing(self):
        return "right" if self.facing_right else "left"

    @property
    def touch_box(self):
        return self.rect.inflate(self.touch_box_margin, self.touch_box_margin)

    def touching(self, entity: Entity):
        return self.touch_box.colliderect(entity.rect)

    def standing_on_platform(self, platform):
        return self.touching(platform) and self.rect.bottom <= platform.rect.top

    @property
    def airborne(self):
        for platform in self.level.platforms:
            if self.standing_on_platform(platform):
                return False
        return True

    def state_fall(self):
        self.image = self.sprites["jump_" + self.facing].get_frame(self.animation_frame)
        input = self.input

        holding_back = (self.facing_right and input.is_down(input.LEFT)) or (
            not self.facing_right and input.is_down(input.RIGHT)
        )
        holding_forward = (self.facing_right and input.is_down(input.RIGHT)) or (
            not self.facing_right and input.is_down(input.LEFT)
        )
        Cstick_left = (
            input.is_pressed(input.C_LEFT)
            and not input.is_pressed(input.C_UP)
            and not input.is_pressed(input.C_DOWN)
        )
        Cstick_right = (
            input.is_pressed(input.C_RIGHT)
            and not input.is_pressed(input.C_UP)
            and not input.is_pressed(input.C_DOWN)
        )
        Cstick_up = (
            input.is_pressed(input.C_UP)
            and not input.is_pressed(input.C_LEFT)
            and not input.is_pressed(input.C_RIGHT)
        )
        Cstick_down = (
            input.is_pressed(input.C_DOWN)
            and not input.is_pressed(input.C_LEFT)
            and not input.is_pressed(input.C_RIGHT)
        )
        Cstick_back = (self.facing_right and Cstick_left) or (
            not self.facing_right and Cstick_right
        )
        Cstick_forward = (self.facing_right and Cstick_right) or (
            not self.facing_right and Cstick_left
        )

        # A-button inputs
        if input.is_pressed(input.A):
            if holding_back:
                self.state = self.BackAir(self)
            elif holding_forward:
                self.state = self.ForwardAir(self)
            elif input.is_down(input.UP):
                self.state = self.UpAir(self)
            elif input.is_down(input.DOWN):
                self.state = self.DownAir(self)
            else:
                self.state = self.NeutralAir(self)

        # C-stick inputs
        if Cstick_up:
            self.state = self.UpAir(self)
        if Cstick_down:
            self.state = self.DownAir(self)
        if Cstick_forward:
            self.state = self.ForwardAir(self)
        if Cstick_back:
            self.state = self.BackAir(self)

        if input.is_pressed(input.Y):
            self.v = -self.jump_speed
            self.fast_fall = False

        # air dodge
        if input.is_pressed(input.R) or input.is_pressed(input.L):
            self.air_dodge()

        self.allow_aerial_drift()
        self.allow_fastfall()
        self.fall_physics()

    def air_dodge(self):
        input = self.input
        x = input.is_down(input.RIGHT) - input.is_down(input.LEFT)
        y = input.is_down(input.DOWN) - input.is_down(input.UP)

        # get unit vector
        v = numpy.array([x, y])
        magnitude = numpy.linalg.norm(v)
        if magnitude == 0:
            self.u = 0
            self.v = 0
        else:
            unit = v / magnitude
            self.u, self.v = unit * self.air_dodge_speed

        self.state = self.state_air_dodge

    def state_air_dodge(self):
        decay = 0.1
        self.u *= 1 - decay
        self.v *= 1 - decay
        """ 
        todo: here do platform collision 
        horizontal collision: 
            droppable: pass through
            solid: set velocity to 0 but stay in airdodge state
        vertical collision: 
            set vertical velocity to 0 but maintain horizontal velocity!
            
        later: build in a buffer so you can be slightly below the top of a platform. 
        """
        # update horizontal position and handle platform collisions
        self.x += self.u
        platforms = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
        for platform in platforms:
            if not platform.droppable:
                self.bump_horizontally(platform)

        # update vertical position and handle platform collisions
        old_rect = Rect(self.rect)  # remember previous position
        self.y += self.v
        platforms = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
        for platform in platforms:
            if platform.droppable:
                self.vertical_collide_droppable_platform(self, platform, old_rect)
            else:
                self.vertical_collide_solid_platform(self, platform)

        if self.game_tick == self.air_dodge_duration:
            self.state = self.state_fall

    def apply_gravity(self, speed_limit):
        self.v += self.acceleration_to_apply(self.v, self.gravity, speed_limit)

    def apply_air_resistance(self):
        magnitude = abs(self.u)
        direction = sign(self.u)
        speed = magnitude - self.air_resistance
        speed = max([0, speed])
        self.u = speed * direction

    def bump_horizontally(self, platform):
        moving_right = self.u > 0
        self.u = 0
        if moving_right:
            self.rect.right = platform.rect.left
        else:
            self.rect.left = platform.rect.right

    def bump_vertically(self, platform):
        moving_down = self.v > 0
        self.v = 0
        if moving_down:
            self.rect.bottom = platform.rect.top
        else:
            self.rect.top = platform.rect.bottom

    def bounce_horizontally(self, platform):
        moving_right = self.u > 0
        if not platform.droppable:
            pass  # you can move horizontally through droppable platforms
        else:
            if moving_right:
                self.rect.right = platform.rect.left
            else:
                self.rect.left = platform.rect.right
            self.u = -self.u * (1 - BOUNCE_LOSS)

    def bounce_vertically(self, platform):
        moving_down = self.v > 0
        if moving_down:
            self.rect.bottom = platform.rect.top
        else:
            self.rect.top = platform.rect.bottom
        self.v = -self.v * (1 - BOUNCE_LOSS)

    @staticmethod
    def horizontal_collide_droppable_platform(self, platform):
        pass  # you can move horizontally through droppable platforms

    @staticmethod
    def horizontal_collide_solid_platform(self, platform):
        return self.bump_horizontally(platform)

    def horizontal_collide_platform(self, platform):
        if platform.droppable:
            return None
        else:
            return self.bump_horizontally(platform)

    def vertical_collide_platform(
        self, platform, old_rect: Rect, allow_fall_through, next_state=None
    ):
        moving_down = self.v > 0
        if moving_down:
            # if character was already inside the platform, or player is holding down
            if (old_rect.bottom > platform.rect.top) or (
                self.input.is_down(self.input.DOWN) and self.state == self.state_fall
            ):
                pass
            # if character was above the platform and not holding down
            else:
                # don't go through the platform
                self.bump_vertically(platform)
                self.state = self.state_stand
                self.fast_fall = False
        else:  # if travelling up
            pass  # you can go upwards through droppable platforms

    @staticmethod
    def vertical_collide_droppable_platform(self, platform, old_rect: Rect):
        # todo: add optional param next_state
        # todo: add param allow_fall_through and merge this with
        moving_down = self.v > 0
        if moving_down:
            # if character was already inside the platform, or player is holding down
            if (old_rect.bottom > platform.rect.top) or (
                self.input.is_down(self.input.DOWN) and self.state == self.state_fall
            ):
                pass
            # if character was above the platform and not holding down
            else:
                # don't go through the platform
                self.bump_vertically(platform)
                self.state = self.state_stand
                self.fast_fall = False
        else:  # if travelling up
            pass  # you can go upwards through droppable platforms

    @staticmethod
    def vertical_collide_solid_platform(self, platform):
        moving_down = self.v > 0
        if moving_down:
            self.rect.bottom = min([self.rect.bottom, platform.rect.top])
            self.v = 0
            self.state = self.state_stand
            self.fast_fall = False
        else:
            self.rect.top = max([self.rect.top, platform.rect.bottom])
            self.v = 0

    def fall_physics(
        self,
        horizontal_collide_droppable_platform=None,
        horizontal_collide_solid_platform=None,
        vertical_collide_droppable_platform=None,
        vertical_collide_solid_platform=None,
    ):
        speed_limit = self.fast_fall_speed if self.fast_fall else self.fall_speed
        self.apply_gravity(speed_limit)
        self.apply_air_resistance()

        if not horizontal_collide_droppable_platform:
            horizontal_collide_droppable_platform = self.horizontal_collide_droppable_platform
        if not horizontal_collide_solid_platform:
            horizontal_collide_solid_platform = self.horizontal_collide_solid_platform
        if not vertical_collide_droppable_platform:
            vertical_collide_droppable_platform = self.vertical_collide_droppable_platform
        if not vertical_collide_solid_platform:
            vertical_collide_solid_platform = self.vertical_collide_solid_platform

        # update horizontal position and handle platform collisions
        self.x += self.u
        platforms = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
        for platform in platforms:
            # todo: what I want here is a function called self.fall_into_platform oid
            if platform.droppable:
                horizontal_collide_droppable_platform(self, platform)
            else:
                horizontal_collide_solid_platform(self, platform)

        # update vertical position and handle platform collisions
        old_rect = Rect(self.rect)  # remember previous position
        self.y += self.v
        platforms = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
        for platform in platforms:
            if platform.droppable:
                vertical_collide_droppable_platform(self, platform, old_rect)
            else:
                vertical_collide_solid_platform(self, platform)

    def grounded_physics(self):
        magnitude = abs(self.u)
        direction = sign(self.u)
        speed = magnitude - self.friction
        speed = speed if speed > 0 else 0
        self.u = speed * direction
        self.x += self.u
        self.y += self.v

    def hit_physics(self):
        # todo: deprecate and use fall_physics instead.
        self.apply_gravity(self.fall_speed)
        self.apply_air_resistance()

        # update horizontal position and handle platform collisions
        self.x += self.u
        platforms = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
        moving_right = self.u > 0
        for plat in platforms:
            if plat.droppable:
                pass  # you can move horizontally through droppable platforms
            else:
                if moving_right:
                    self.rect.right = min([self.rect.right, plat.rect.left])
                else:
                    self.rect.left = max([self.rect.left, plat.rect.right])
                self.u = -self.u * (1 - BOUNCE_LOSS)

        # update vertical position and handle platform collisions
        old_rect = Rect(self.rect)  # remember previous position
        self.y += self.v
        platforms = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
        moving_down = self.v > 0
        for plat in platforms:
            # droppable platforms
            if plat.droppable:
                if moving_down:
                    # if character was already inside the platform
                    if old_rect.bottom > plat.rect.top:
                        pass
                    # if character was above the platform
                    else:
                        # don't go through the platform
                        self.rect.bottom = min([self.rect.bottom, plat.rect.top])
                        self.v = -self.v * (1 - BOUNCE_LOSS)
                else:  # if travelling up
                    pass  # you can go upwards through droppable platforms

            # solid platforms
            else:
                if moving_down:
                    self.rect.bottom = min([self.rect.bottom, plat.rect.top])
                    self.v = -self.v * (1 - BOUNCE_LOSS)
                else:
                    self.rect.top = max([self.rect.top, plat.rect.bottom])
                    self.v = -self.v * (1 - BOUNCE_LOSS)

    def state_stand(self):
        self.image = self.sprites["stand_" + self.facing].get_frame(self.animation_frame)
        input = self.input

        if input.is_pressed(input.DOWN):
            platforms = list(filter(self.standing_on_platform, self.level.platforms))
            if all(platform.droppable for platform in platforms):
                self.y += 1  # need this to drop through platforms

        if input.is_down(input.DOWN):
            self.state = self.state_crouch

        if input.is_down(input.LEFT) or input.is_down(input.RIGHT):
            self.state = self.state_initial_dash

        if input.is_pressed(input.Y):
            self.state = self.state_jumpsquat
        if self.airborne:
            self.state = self.state_fall
        if input.is_pressed(input.X):
            self.state = self.AttackMove(self)
        if input.is_down(input.UP) and input.is_pressed(input.A):
            self.state = self.UpTilt(self)

        self.grounded_physics()

    def enter_hitpause(self):
        """Using a closure to store this state. This is a good idea because it still allows easy
        access to the self variable, unlike class-based states."""
        return_state = self.state
        return_tick = self.game_tick

        def hitpause():
            if self.hitpause_duration == 0:
                self.state = return_state
                self.game_tick = return_tick
            else:
                self.hitpause_duration -= 1

        self.state = hitpause

    def state_initial_dash(self):
        self.image = self.sprites["run_" + self.facing].get_frame(0)
        input = self.input
        if input.is_down(input.LEFT):
            if self.facing_right:
                self.game_tick = 0  # reset state counter
            self.facing_right = False
            self.u = -self.run_speed
        if input.is_down(input.RIGHT):
            if not self.facing_right:
                self.game_tick = 0
            self.facing_right = True
            self.u = self.run_speed
        if input.is_pressed(input.Y):
            self.state = self.state_jumpsquat
        if input.is_down(input.DOWN):
            self.state = self.state_crouch
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.state_fall
        if self.game_tick == self.initial_dash_duration:
            self.state = self.state_run
        self.grounded_physics()

    def state_run(self):
        self.image = self.sprites["run_" + self.facing].get_frame(self.animation_frame)
        input = self.input
        if not input.is_down(input.LEFT) and not input.is_down(input.RIGHT):
            self.state = self.state_run_end
        if input.is_down(input.LEFT):
            if self.facing_right:
                self.state = self.state_run_turnaround
            else:
                self.u = -self.run_speed
            self.facing_right = False
        if input.is_down(input.RIGHT):
            if not self.facing_right:
                self.state = self.state_run_turnaround
            else:
                self.u = self.run_speed
            self.facing_right = True
        if input.is_pressed(input.Y):
            self.state = self.state_jumpsquat
        if input.is_down(input.DOWN):
            self.state = self.state_crouch
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.state_fall
        self.grounded_physics()

    def state_run_turnaround(self):
        self.image = self.sprites["crouch_" + self.facing].get_frame(self.animation_frame)
        input = self.input
        if input.is_pressed(input.Y):
            self.state = self.state_jumpsquat
        if input.is_down(input.DOWN):
            self.state = self.state_crouch
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.state_fall
        if self.game_tick == self.run_turnaround_duration:
            self.state = self.state_stand
        self.grounded_physics()

    def state_run_end(self):
        self.image = self.sprites["crouch_" + self.facing].get_frame(self.animation_frame)
        input = self.input
        if input.is_pressed(input.Y):
            self.state = self.state_jumpsquat
        if input.is_down(input.DOWN):
            self.state = self.state_crouch
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.state_fall
        if self.game_tick == self.run_turnaround_duration:
            self.state = self.state_stand
        self.grounded_physics()

    def state_jumpsquat(self):
        self.image = self.sprites["crouch_" + self.facing].get_frame(self.animation_frame)
        if self.game_tick == self.jumpsquat_frames:
            if self.input.is_down(self.input.Y):
                self.jump()
            else:
                self.shorthop()

        self.grounded_physics()

    def state_crouch(self):
        self.image = self.sprites["crouch_" + self.facing].get_frame(self.animation_frame)
        input = self.input
        if self.airborne:
            self.state = self.state_fall
        if input.is_pressed(input.Y):
            self.jump()
        if not input.is_down(input.DOWN):
            self.state = self.state_stand
        self.grounded_physics()

    def jump(self):
        self.v = -self.jump_speed
        self.state = self.state_fall
        self.fastfall = False

    def shorthop(self):
        self.v = -self.shorthop_speed
        self.state = self.state_fall
        self.fastfall = False

    def handle_hit(self, hitbox):
        self.state = self.state_hit_aerial
        sounds.hit.play()

    def allow_fastfall(self):
        input = self.input
        if input.is_pressed(input.DOWN) and self.v > 0 and not self.fast_fall:
            # self.level.add_particle_effect(JumpRing(*self.rect.midbottom, color=Color("orange")))
            self.fast_fall = True
            self.v = self.fast_fall_speed

    def allow_hitfall(self):
        input = self.input
        if input.is_down(input.DOWN) and self.hitpause_duration > 0:
            self.fast_fall = True
            self.v = self.fast_fall_speed

    def enforce_max_fall_speed(self):
        if self.v > 0 and abs(self.v) > self.fall_speed:
            self.v = self.fall_speed

    def allow_aerial_drift(self):
        input = self.input
        if input.is_down(input.LEFT):
            self.u -= self.acceleration_to_apply(-self.u, self.air_acceleration, self.air_speed)
        if input.is_down(input.RIGHT):
            self.u += self.acceleration_to_apply(self.u, self.air_acceleration, self.air_speed)

    def landing_lag(self, ticks):
        def func():
            self.image = self.sprites["crouch_" + self.facing].get_frame(self.animation_frame)
            if self.game_tick == ticks:
                self.state = self.state_stand

        return func

    def state_hit_aerial(self):
        self.image = Surface((50, 50))
        self.image.fill(Color("red"))
        if self.hitstun_duration == 0:
            self.state = self.state_fall
        else:
            self.hitstun_duration -= 1
        if not self.airborne:
            self.state = self.state_stand
        self.hit_physics()

    @staticmethod
    def acceleration_to_apply(speed, acceleration, speed_limit):
        """ everything must be > 0 """
        if speed + acceleration <= speed_limit:
            return acceleration
        else:
            difference = speed_limit - speed
            if difference > 0:
                return difference
        return 0


class Move:
    """ E.g. an attack """

    hitbox_mapping: dict
    character: Character

    def __init__(self, character: Character):
        # todo: make a frame mapping similar to the hitbox mapping.
        self.character = character
        if not character.facing_right:
            hitboxes = {h for frame, hitboxes in self.hitbox_mapping.items() for h in hitboxes}
            for hitbox in hitboxes:
                hitbox.flip_x()
        self.hitbox_lookup = {
            frame: hitboxes
            for frames, hitboxes in self.hitbox_mapping.items()
            for frame in ([frames] if isinstance(frames, int) else range(frames[0], frames[-1] + 1))
        }
        sounds.captain_falcon.swing.play()

    def __call__(self, *args, **kwargs):
        n = self.character.animation_frame
        active_hitboxes = self.hitbox_lookup.get(n, [])
        for hitbox in active_hitboxes:
            self.character.level.add_hitbox(hitbox)


class AerialMove(Move):
    landing_lag: int

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        self.character.allow_fastfall()
        self.character.allow_aerial_drift()
        self.character.allow_hitfall()
        if not self.character.airborne:
            self.character.state = self.character.landing_lag(self.landing_lag)

        self.character.fall_physics(
            horizontal_collide_droppable_platform=self.horizontal_collide_droppable_platform,
            horizontal_collide_solid_platform=self.horizontal_collide_solid_platform,
            vertical_collide_droppable_platform=self.vertical_collide_droppable_platform,
            vertical_collide_solid_platform=self.vertical_collide_solid_platform,
        )

    @classmethod
    def horizontal_collide_droppable_platform(cls, character, platform):
        pass  # you can move horizontally through droppable platforms

    @classmethod
    def horizontal_collide_solid_platform(cls, character: Character, platform: Platform):
        moving_right = character.u > 0
        if moving_right:
            character.rect.right = min([character.rect.right, platform.rect.left])
        else:
            character.rect.left = max([character.rect.left, platform.rect.right])
        character.u = 0

    @classmethod
    def vertical_collide_droppable_platform(
        cls,
        character: Character,
        platform: Platform,
        old_rect,
    ):
        moving_down = character.v > 0
        if moving_down:
            # if character was already inside the platform, or player is holding down
            if (old_rect.bottom > platform.rect.top) or (
                character.input.is_down(character.input.DOWN)
                and character.state == character.state_fall
            ):
                pass
            # if character was above the platform and not holding down
            else:
                # don't go through the platform
                character.rect.bottom = min([character.rect.bottom, platform.rect.top])
                character.v = 0
                character.state = character.landing_lag(cls.landing_lag)
                character.fast_fall = False
        else:  # if travelling up
            pass  # you can go upwards through droppable platforms

    @classmethod
    def vertical_collide_solid_platform(cls, character: Character, platform: Platform):
        moving_down = character.v > 0
        if moving_down:
            character.rect.bottom = min([character.rect.bottom, platform.rect.top])
            character.v = 0
            character.state = character.landing_lag(cls.landing_lag)
            character.fast_fall = False
        else:
            character.rect.top = max([character.rect.top, platform.rect.bottom])
            character.v = 0


class Hitbox(Entity):
    """
    A hitbox always has an owner. It follows its owner's x/y position. The x/y_offset attributes
    allow us to position the hitbox relative to its owner.
    """

    debug_color = (60, 0, 0)

    def __init__(
        self,
        owner: Entity,
        width: int,
        height: int,
        x_offset: int = 0,
        y_offset: int = 0,
        rotation: float = 0,
        base_knockback: float = 0,
        fixed_knockback: float = 0,
        knockback_growth: float = 0,
        knockback_angle: float = 0,
        damage: float = 0,
        higher_priority_sibling: Entity = None,
        lower_priority_sibling: Entity = None,
    ):
        super().__init__()
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.owner = owner
        self.width = width
        self.height = height
        self.rect = Rect(0, 0, self.width, self.height)
        self.rotation = rotation
        self.damage = damage
        self.base_knockback = base_knockback
        self.fixed_knockback = fixed_knockback
        self.knockback_angle = knockback_angle
        self.knockback_growth = knockback_growth
        self.higher_priority_sibling = higher_priority_sibling
        self.lower_priority_sibling = lower_priority_sibling

        self.image = self.create_image()

    def create_image(self):
        image = pygame.Surface((self.width, self.height))
        pygame.draw.ellipse(image, self.debug_color, (0, 0, self.width, self.height))
        image.set_colorkey((0, 0, 0))
        image = pygame.transform.rotate(image, self.rotation)
        return image

    def __repr__(self):
        return f"Hitbox with id {id(self)}"

    def handle_hit(self, object, knockback):
        """Object is the entity hit by this hitbox. I've passed it here so that hitboxes can do
        context specific stuff e.g. trigger the object's "electrocute" animation if the hitbox is
        electric"""
        self.level.screen_shake += 10
        self.owner.hitpause_duration = self.hitpause_duration
        self.owner.enter_hitpause()
        object.hitpause_duration = self.hitpause_duration
        object.hitstun_duration = self.hitstun_duration(knockback)
        object.y -= 1

    @property
    def hitpause_duration(self):
        return round(
            (self.fixed_knockback + self.base_knockback + self.knockback_growth) * HITPAUSE_CONSTANT
        )

    def hitstun_duration(self, knockback):
        return round(knockback * HITSTUN_CONSTANT)

    @property
    def rect(self):
        """If the hitbox has an owner, it will follow its owner's x and y (offset by x_offset
        and y_offset)."""
        self.align_to_owner()
        return self._rect

    @rect.setter
    def rect(self, new_rect):
        self._rect = new_rect
        self.align_to_owner()

    def align_to_owner(self):
        self._rect.center = (
            self.owner.x + self.x_offset,
            self.owner.y + self.y_offset,
        )

    def draw(self, surface, debug=False):
        if debug:
            image_rect = self.image.get_rect()
            image_rect.center = self.rect.center
            surface.blit(self.image, image_rect, special_flags=pygame.BLEND_RGB_ADD)
            if self.knockback_angle is not None:
                draw_arrow(surface, self.rect.center, self.knockback_angle, (255, 0, 0), 100)

    def flip_x(self):
        self.knockback_angle = 180 - self.knockback_angle
        self.rotation = 180 - self.rotation
        self.x_offset = -self.x_offset
        self.image = self.create_image()

    @property
    def lower_priority_sibling(self):
        return self._lower_priority_sibling

    @lower_priority_sibling.setter
    def lower_priority_sibling(self, hitbox):
        self._lower_priority_sibling = hitbox
        if hitbox:
            hitbox._higher_priority_sibling = self

    @property
    def higher_priority_sibling(self):
        return self._higher_priority_sibling

    @higher_priority_sibling.setter
    def higher_priority_sibling(self, hitbox):
        self._higher_priority_sibling = hitbox
        if hitbox:
            hitbox._lower_priority_sibling = self

    @property
    def lower_priority_siblings(self) -> {"Hitbox"}:
        sibling = self.lower_priority_sibling
        return {sibling} | sibling.lower_priority_siblings if sibling else set()

    @property
    def higher_priority_siblings(self) -> {"Hitbox"}:
        sibling = self.higher_priority_sibling
        return {sibling} | sibling.higher_priority_siblings if sibling else set()

    @property
    def siblings(self):
        return self.higher_priority_siblings | self.lower_priority_siblings


def handle_hitbox_collision(hitbox: Hitbox, object):
    # here's where we calculate how far/fast the object gets knocked
    object.damage += hitbox.damage  # important for charged smashes
    # fixed knockback is affected by nothing
    fixed_knockback_term = hitbox.fixed_knockback
    # base knockback and growing knockback are both affected by target weight
    base_knockback_term = hitbox.base_knockback / object.mass
    knockback_growth_term = hitbox.knockback_growth * object.damage / object.mass / 10
    knockback = fixed_knockback_term + base_knockback_term + knockback_growth_term
    u = knockback * numpy.cos(numpy.deg2rad(hitbox.knockback_angle))
    v = -knockback * numpy.sin(numpy.deg2rad(hitbox.knockback_angle))
    object.u = round(u)
    object.v = round(v)

    # object-specific effects
    object.handle_hit(hitbox)
    hitbox.handle_hit(object, knockback)


class HitHandler:
    def __init__(self):
        # queue for storing
        self.handled = deque(maxlen=200)

    def handle_hits(self, hitboxes: [Hitbox], objects: [Entity]):
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

                # if this hitbox has already affected the object, don't repeat the interaction
                if (hitbox, object) in self.handled:
                    continue

                # if the hitbox has higher-priority siblings that are also colliding, skip and
                # let the higher-priority hitbox collide instead
                if any(s in colliding_hitboxes for s in hitbox.higher_priority_siblings):
                    continue

                handle_hitbox_collision(hitbox, object)
                self.handled.append((hitbox, object))
                # if the hitbox has lower priority sibling hitboxes, add those to the handled
                # list so that they don't also hit the object
                for sibling in hitbox.siblings:
                    self.handled.append((sibling, object))
