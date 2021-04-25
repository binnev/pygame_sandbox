from numpy import sign
import numpy
import pygame
from pygame import Color, Surface
from pygame.rect import Rect

from base.animation import SpriteDict
from fighting_game import sounds
from fighting_game.conf import BOUNCE_LOSS
from fighting_game.inputs import GamecubeController
from fighting_game.objects import PhysicalEntity
from fighting_game.platforms import Platform


class Character(PhysicalEntity):
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

    ForwardAir: "Move"
    BackAir: "Move"
    UpAir: "Move"
    DownAir: "Move"
    NeutralAir: "Move"
    UpSmash: "Move"
    DownSmash: "Move"
    ForwardSmash: "Move"
    DashAttack: "Move"
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

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        # draw touchbox
        if debug:
            pygame.draw.rect(surface, Color("goldenrod"), self.touch_box, 1)

    @property
    def facing(self):
        return "right" if self.facing_right else "left"

    @property
    def touch_box(self):
        return self.rect.inflate(self.touch_box_margin, self.touch_box_margin)

    def touching(self, entity: PhysicalEntity):
        return self.touch_box.colliderect(entity.rect)

    def standing_on_platform(self, platform):
        return self.touching(platform) and self.rect.bottom <= platform.rect.top

    @property
    def airborne(self):
        for platform in self.level.platforms:
            if self.standing_on_platform(platform):
                return False
        return True

    def state_stand(self):
        self.image = self.sprites["stand_" + self.facing].get_frame(self.animation_frame)

        self.allow_platform_drop()
        self.allow_jump()
        self.allow_crouch()
        self.allow_dash()

        self.allow_jab()

        self.allow_up_tilt()
        self.allow_down_tilt()
        self.allow_forward_tilt()

        self.allow_down_smash()
        self.allow_up_smash()
        self.allow_forward_smash()

        if self.airborne:
            self.state = self.state_fall

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

        self.allow_up_smash()
        self.allow_down_smash()
        self.allow_forward_smash()
        self.allow_dash_attack()

        self.grounded_physics()

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

        if self.tick == self.air_dodge_duration:
            self.state = self.state_fall

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

    def state_initial_dash(self):
        self.image = self.sprites["run_" + self.facing].get_frame(0)
        input = self.input
        if input.is_down(input.LEFT):
            if self.facing_right:
                self.tick = 0  # reset state counter
            self.facing_right = False
            self.u = -self.run_speed
        if input.is_down(input.RIGHT):
            if not self.facing_right:
                self.tick = 0
            self.facing_right = True
            self.u = self.run_speed
        if input.is_pressed(input.Y):
            self.state = self.state_jumpsquat
        if input.is_down(input.DOWN):
            self.state = self.state_crouch
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.state_fall
        if self.tick == self.initial_dash_duration:
            self.state = self.state_run

        self.allow_up_smash()
        self.allow_down_smash()
        self.allow_forward_smash()
        self.allow_dash_attack()

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
        if self.tick == self.run_turnaround_duration:
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
        if self.tick == self.run_turnaround_duration:
            self.state = self.state_stand
        self.grounded_physics()

    def state_jumpsquat(self):
        self.image = self.sprites["crouch_" + self.facing].get_frame(self.animation_frame)
        if self.tick == self.jumpsquat_frames:
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
        if not input.is_down(input.DOWN):
            self.state = self.state_stand

        self.allow_jump()

        self.allow_down_tilt()

        self.allow_down_smash()
        self.allow_up_smash()
        self.allow_forward_smash()

        self.grounded_physics()

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

    def do_move(self, move):
        self.state = move(self)

    def enter_hitpause(self):
        """Using a closure to store this state. This is a good idea because it still allows easy
        access to the self variable, unlike class-based states."""
        return_state = self.state
        return_tick = self.tick

        def hitpause():
            if self.hitpause_duration == 0:
                self.state = return_state
                self.tick = return_tick
            else:
                self.hitpause_duration -= 1

        self.state = hitpause

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

    def allow_down_smash(self):
        input = self.input
        if input.is_pressed(input.C_DOWN):
            self.do_move(self.DownSmash)

    def allow_up_smash(self):
        input = self.input
        if input.is_pressed(input.C_UP):
            self.do_move(self.UpSmash)

    def allow_forward_smash(self):
        input = self.input
        if input.is_pressed(input.C_LEFT) or input.is_pressed(input.C_RIGHT):
            if input.is_down(input.C_RIGHT):
                self.facing_right = True
            if input.is_down(input.C_LEFT):
                self.facing_right = False
            self.do_move(self.ForwardSmash)

    def allow_dash_attack(self):
        input = self.input
        if (input.is_down(input.LEFT) or input.is_down(input.RIGHT)) and input.is_pressed(input.A):
            self.do_move(self.DashAttack)

    def allow_up_tilt(self):
        input = self.input
        if input.is_down(input.UP) and input.is_pressed(input.A):
            self.do_move(self.UpTilt)

    def allow_down_tilt(self):
        input = self.input
        if input.is_down(input.DOWN) and input.is_pressed(input.A):
            if input.is_down(input.RIGHT):
                self.facing_right = True
            if input.is_down(input.LEFT):
                self.facing_right = False
            self.do_move(self.DownTilt)

    def allow_forward_tilt(self):
        input = self.input
        if (input.is_down(input.LEFT) or input.is_down(input.RIGHT)) and input.is_pressed(input.A):
            if input.is_down(input.RIGHT):
                self.facing_right = True
            if input.is_down(input.LEFT):
                self.facing_right = False
            self.do_move(self.ForwardTilt)

    def allow_platform_drop(self):
        input = self.input
        if input.is_pressed(input.DOWN):
            platforms = list(filter(self.standing_on_platform, self.level.platforms))
            if all(platform.droppable for platform in platforms):
                self.y += 1  # need this to drop through platforms

    def allow_jab(self):
        input = self.input
        if (
            input.is_pressed(input.A)
            and not input.is_down(input.LEFT)
            and not input.is_down(input.RIGHT)
            and not input.is_down(input.UP)
            and not input.is_down(input.DOWN)
        ):
            self.do_move(self.Jab)

    def allow_jump(self):
        input = self.input
        if input.is_pressed(input.Y) or input.is_pressed(input.X):
            if self.airborne:
                if input.is_pressed(input.Y):
                    self.v = -self.jump_speed
                    self.fast_fall = False
            else:
                self.state = self.state_jumpsquat

    def allow_dash(self):
        input = self.input
        if input.is_pressed(input.LEFT) or input.is_pressed(input.RIGHT):
            self.state = self.state_initial_dash

    def allow_crouch(self):
        input = self.input
        if input.is_down(input.DOWN):
            self.state = self.state_crouch

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
            if self.tick == ticks:
                self.state = self.state_stand

        return func

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
    hitbox_mapping: dict
    character: Character
    sound = sounds.swing5
    sprite_name: str = ""
    frame_mapping: list

    def __init__(self, character: Character):
        self.character = character
        if not character.facing_right:
            # This needs to be a set because we want to flip each hitbox exactly once
            hitboxes = {h for item in self.frame_mapping for h in item.get("hitboxes", [])}
            for hitbox in hitboxes:
                hitbox.flip_x()
        self.sound.play()

    def __call__(self, *args, **kwargs):
        n = self.character.animation_frame
        try:
            frame_data = self.frame_mapping[n]
        except IndexError:
            return self.end()

        image = frame_data.get("image")
        if image:
            self.character.image = image
        active_hitboxes = frame_data.get("hitboxes", [])
        for hitbox in active_hitboxes:
            self.character.level.add_hitbox(hitbox)

        # only handle grounded physics; AerialMove will handle airborne physics
        if not self.character.airborne:
            self.character.grounded_physics()

    def end(self):
        self.character.state = self.character.state_stand
        return self.character.state()  # execute the state


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

    def end(self):
        self.character.state = self.character.state_fall
        return self.character.state()  # execute the state

    # todo: move these (and the responsibility for choosing which to use) onto Character. Then
    #  merge AerialMove and Move.

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
