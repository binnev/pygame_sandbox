import numpy
import pygame
from numpy import sign
from pygame import Color, Surface
from pygame.rect import Rect

from base.animation import SpriteDict
from base.inputs.gamecube import GamecubeController
from fighting_game import sounds
from fighting_game.conf import BOUNCE_LOSS
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
    aerial_jump_speed: float
    shorthop_speed: float
    gravity: float
    friction: float
    air_resistance: float
    fall_speed: float
    fast_fall_speed: float
    fast_fall: bool
    jumpsquat_frames: int
    max_aerial_jumps: int = 1  # how many aerial jumps can the character do
    max_air_dodges: int = 1
    max_wall_jumps: int = 1
    aerial_jumps: int  # how many aerial jumps does the character have left
    air_dodges: int
    wall_jumps: int

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
    GroundedNeutralB: "Move"
    GroundedSideB: "Move"
    GroundedUpB: "Move"
    GroundedDownB: "Move"
    AerialNeutralB: "Move"
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
        self.aerial_jumps = self.max_aerial_jumps
        self.air_dodges = self.max_air_dodges
        self.wall_jumps = self.max_wall_jumps

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
        return (
            self.touching(platform)
            and self.rect.bottom <= platform.rect.top
            and self.v >= 0  # don't snap to platforms when jumping through them
        )

    def touching_side_of_platform(self, platform):
        return self.touching(platform) and (
            self.rect.right <= platform.rect.left or self.rect.left >= platform.rect.right
        )

    @property
    def airborne(self):
        for platform in self.level.platforms:
            if self.standing_on_platform(platform):
                return False
        return True

    def state_stand(self):
        self.image = self.sprites["stand_" + self.facing].loop(self.animation_frame)
        self.aerial_jumps = self.max_aerial_jumps
        self.air_dodges = self.max_air_dodges
        self.wall_jumps = self.max_wall_jumps

        if self.airborne:
            self.state = self.state_fall

        # B-button inputs
        input = self.input
        if input.B.is_pressed:
            if input.UP:
                self.y -= 1
                self.allow_aerial_up_b()
            elif input.LEFT:
                self.facing_right = False
                self.do_move(self.AerialNeutralB)
            elif input.RIGHT:
                self.facing_right = True
                self.do_move(self.AerialNeutralB)
            else:
                self.do_move(self.AerialNeutralB)

        self.allow_platform_drop()
        self.allow_grounded_jump()
        self.allow_crouch()
        self.allow_dash()

        self.allow_jab()

        self.allow_up_tilt()
        self.allow_down_tilt()
        self.allow_forward_tilt()

        self.allow_down_smash()
        self.allow_up_smash()
        self.allow_forward_smash()

        self.grounded_physics()

    def state_run(self):
        self.image = self.sprites["run_" + self.facing].loop(self.animation_frame)
        input = self.input
        if not input.LEFT and not input.RIGHT:
            self.state = self.state_run_end
        if input.LEFT:
            if self.facing_right:
                self.state = self.state_run_turnaround
            else:
                self.u = -self.run_speed
            self.facing_right = False
        if input.RIGHT:
            if not self.facing_right:
                self.state = self.state_run_turnaround
            else:
                self.u = self.run_speed
            self.facing_right = True
        if input.Y.is_pressed:
            self.state = self.state_jumpsquat
        if input.DOWN:
            self.state = self.state_crouch
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.state_fall

        self.allow_up_smash()
        self.allow_down_smash()
        self.allow_forward_smash()
        self.allow_dash_attack()

        self.grounded_physics()

    def state_fall(self):
        self.image = self.sprites["fall_" + self.facing].loop(self.animation_frame)
        input = self.input
        holding_back = (self.facing_right and input.LEFT) or (not self.facing_right and input.RIGHT)

        holding_forward = (self.facing_right and input.RIGHT) or (
            not self.facing_right and input.LEFT
        )

        Cstick_left = (
            input.C_LEFT.is_pressed and not input.C_UP.is_pressed and not input.C_DOWN.is_pressed
        )
        Cstick_right = (
            input.C_RIGHT.is_pressed and not input.C_UP.is_pressed and not input.C_DOWN.is_pressed
        )
        Cstick_up = (
            input.C_UP.is_pressed and not input.C_LEFT.is_pressed and not input.C_RIGHT.is_pressed
        )
        Cstick_down = (
            input.C_DOWN.is_pressed and not input.C_LEFT.is_pressed and not input.C_RIGHT.is_pressed
        )
        Cstick_back = (self.facing_right and Cstick_left) or (
            not self.facing_right and Cstick_right
        )
        Cstick_forward = (self.facing_right and Cstick_right) or (
            not self.facing_right and Cstick_left
        )

        # A-button inputs
        if input.A.is_pressed:
            if holding_back:
                self.do_move(self.BackAir)
            elif holding_forward:
                self.do_move(self.ForwardAir)
            elif input.UP:
                self.do_move(self.UpAir)
            elif input.DOWN:
                self.do_move(self.DownAir)
            else:
                self.do_move(self.NeutralAir)

        # B-button inputs
        if input.B.is_pressed:
            if input.UP:
                self.allow_aerial_up_b()
            elif input.LEFT:
                self.facing_right = False
                self.do_move(self.AerialNeutralB)
            elif input.RIGHT:
                self.facing_right = True
                self.do_move(self.AerialNeutralB)
            else:
                self.do_move(self.AerialNeutralB)

        # C-stick inputs
        if Cstick_up:
            self.do_move(self.UpAir)
        if Cstick_down:
            self.do_move(self.DownAir)
        if Cstick_forward:
            self.do_move(self.ForwardAir)
        if Cstick_back:
            self.do_move(self.BackAir)

        self.allow_air_dodge()
        self.allow_aerial_drift()
        self.allow_fastfall()
        self.fall_physics()
        did_wall_jump = self.allow_wall_jump()
        if not did_wall_jump:
            self.allow_aerial_jump()

    def state_special_fall(self):
        self.image = self.sprites["stomp_" + self.facing].play(2)
        self.allow_aerial_drift()
        self.allow_wall_jump()
        self.fall_physics()

    def state_air_dodge(self):
        # todo: build in a buffer so you can be slightly below the top of a platform.
        decay = 0.1
        self.u *= 1 - decay
        self.v *= 1 - decay
        self.image = self.sprites["air_dodge_" + self.facing].play(0)
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
        self.image.fill(Color("orange"))
        if self.hitstun_duration == 0:
            self.state = self.state_fall
        else:
            self.hitstun_duration -= 1
        self.hit_physics()

    def state_initial_dash(self):
        self.image = self.sprites["run_" + self.facing].play(0)
        input = self.input
        if input.LEFT:
            if self.facing_right:
                self.tick = 0  # reset state counter
            self.facing_right = False
            self.u = -self.run_speed
        if input.RIGHT:
            if not self.facing_right:
                self.tick = 0
            self.facing_right = True
            self.u = self.run_speed
        if input.Y.is_pressed:
            self.state = self.state_jumpsquat
        if input.DOWN:
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
        self.image = self.sprites["crouch_" + self.facing].loop(self.animation_frame)
        input = self.input
        if input.Y.is_pressed:
            self.state = self.state_jumpsquat
        if input.DOWN:
            self.state = self.state_crouch
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.state_fall
        if self.tick == self.run_turnaround_duration:
            self.state = self.state_stand
        self.grounded_physics()

    def state_run_end(self):
        self.image = self.sprites["crouch_" + self.facing].loop(self.animation_frame)
        input = self.input
        if input.Y.is_pressed:
            self.state = self.state_jumpsquat
        if input.DOWN:
            self.state = self.state_crouch
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.state_fall
        if self.tick == self.run_turnaround_duration:
            self.state = self.state_stand
        self.grounded_physics()

    def state_jumpsquat(self):
        self.image = self.sprites["crouch_" + self.facing].loop(self.animation_frame)
        if self.tick == self.jumpsquat_frames:
            if self.input.Y:
                self.grounded_jump()
            else:
                self.shorthop()

        self.grounded_physics()

    def state_wall_jumpsquat(self):
        self.image = self.sprites["crouch_" + self.facing].loop(self.animation_frame)
        if self.tick == self.jumpsquat_frames:
            self.wall_jump()

    def state_crouch(self):
        self.image = self.sprites["crouch_" + self.facing].loop(self.animation_frame)
        input = self.input
        if self.airborne:
            self.state = self.state_fall
        if not input.DOWN:
            self.state = self.state_stand

        self.allow_grounded_jump()

        self.allow_down_tilt()

        self.allow_down_smash()
        self.allow_up_smash()
        self.allow_forward_smash()

        self.grounded_physics()

    def air_dodge(self):
        input = self.input
        x = input.RIGHT - input.LEFT
        y = input.DOWN - input.UP

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
        self.air_dodges -= 1

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
                self.input.DOWN and self.state == self.state_fall
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
                self.input.DOWN and self.state == self.state_fall
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
            self.image = Surface((50, 50))
            self.image.fill(Color("red"))

            if self.hitpause_duration == 0:
                self.state = return_state
                self.tick = return_tick
            else:
                self.hitpause_duration -= 1

        self.state = hitpause

    def grounded_jump(self):
        self.v = -self.jump_speed
        self.state = self.state_fall
        self.fastfall = False

    def shorthop(self):
        self.v = -self.shorthop_speed
        self.state = self.state_fall
        self.fastfall = False

    def wall_jump(self):
        self.u = 5 if self.facing_right else -5
        self.v = -self.jump_speed
        self.fastfall = False
        self.state = self.state_fall
        self.wall_jumps -= 1

    def aerial_jump(self):
        self.v = -self.aerial_jump_speed
        self.state = self.state_fall
        self.fastfall = False
        self.aerial_jumps -= 1

    def handle_get_hit(self, hitbox):
        """ What to do when self gets hit by a hitbox. """
        # here's where we calculate how far/fast the object gets knocked
        self.damage += hitbox.damage  # important for charged smashes
        # fixed knockback is affected by nothing
        fixed_knockback_term = hitbox.fixed_knockback
        # base knockback and growing knockback are both affected by target mass
        base_knockback_term = hitbox.base_knockback / self.mass
        knockback_growth_term = hitbox.knockback_growth * self.damage / self.mass / 10
        knockback = fixed_knockback_term + base_knockback_term + knockback_growth_term
        u = knockback * numpy.cos(numpy.deg2rad(hitbox.knockback_angle))
        v = -knockback * numpy.sin(numpy.deg2rad(hitbox.knockback_angle))
        self.u = round(u)
        self.v = round(v)
        self.hitpause_duration = hitbox.hitpause_duration
        self.hitstun_duration = hitbox.hitstun_duration(knockback)
        self.y -= 1
        self.state = self.state_hit_aerial
        self.enter_hitpause()

    def handle_land_hit(self, hitbox):
        self.hitpause_duration = hitbox.hitpause_duration
        self.enter_hitpause()

    def allow_fastfall(self):
        input = self.input
        if input.DOWN.is_pressed and self.v > 0 and not self.fast_fall:
            # self.level.add_particle_effect(JumpRing(*self.rect.midbottom, color=Color("orange")))
            self.fast_fall = True
            self.v = self.fast_fall_speed

    def allow_hitfall(self):
        input = self.input
        if input.DOWN and self.hitpause_duration > 0:
            self.fast_fall = True
            self.v = self.fast_fall_speed

    def allow_down_smash(self):
        input = self.input
        if input.C_DOWN.is_pressed:
            self.do_move(self.DownSmash)

    def allow_up_smash(self):
        input = self.input
        if input.C_UP.is_pressed:
            self.do_move(self.UpSmash)

    def allow_forward_smash(self):
        input = self.input
        if input.C_LEFT.is_pressed or input.C_RIGHT.is_pressed:
            if input.C_RIGHT:
                self.facing_right = True
            if input.C_LEFT:
                self.facing_right = False
            self.do_move(self.ForwardSmash)

    def allow_dash_attack(self):
        input = self.input
        if (input.LEFT or input.RIGHT) and input.A.is_pressed:
            self.do_move(self.DashAttack)

    def allow_up_tilt(self):
        input = self.input
        if input.UP and input.A.is_pressed:
            self.do_move(self.UpTilt)

    def allow_down_tilt(self):
        input = self.input
        if input.DOWN and input.A.is_pressed:
            if input.RIGHT:
                self.facing_right = True
            if input.LEFT:
                self.facing_right = False
            self.do_move(self.DownTilt)

    def allow_forward_tilt(self):
        input = self.input
        if (input.LEFT or input.RIGHT) and input.A.is_pressed:
            if input.RIGHT:
                self.facing_right = True
            if input.LEFT:
                self.facing_right = False
            self.do_move(self.ForwardTilt)

    def allow_platform_drop(self):
        input = self.input
        if input.DOWN.is_pressed:
            platforms = list(filter(self.standing_on_platform, self.level.platforms))
            if all(platform.droppable for platform in platforms):
                self.y += 1  # need this to drop through platforms

    def allow_jab(self):
        input = self.input
        if (
            input.A.is_pressed
            and not input.LEFT
            and not input.RIGHT
            and not input.UP
            and not input.DOWN
        ):
            self.do_move(self.Jab)

    def allow_grounded_jump(self):
        input = self.input
        if not self.airborne and (input.Y.is_pressed or input.X.is_pressed):
            self.state = self.state_jumpsquat

    def allow_aerial_jump(self):
        input = self.input
        if self.airborne and self.aerial_jumps > 0 and (input.Y.is_pressed or input.X.is_pressed):
            self.aerial_jump()

    def allow_wall_jump(self):
        input = self.input
        platforms = [
            platform
            for platform in self.level.platforms
            if self.touching_side_of_platform(platform)
        ]
        if (input.Y.is_pressed or input.X.is_pressed) and self.wall_jumps > 0 and any(platforms):
            # if the platform is to the left, face right (jumping away from wall)
            if platforms[0].rect.centerx < self.x:
                self.facing_right = True
            else:
                self.facing_right = False
            self.v = 0
            self.state = self.state_wall_jumpsquat
            return True

    def allow_air_dodge(self):
        if self.input.R.is_pressed or self.input.L.is_pressed and self.air_dodges > 0:
            self.air_dodge()

    def allow_dash(self):
        if self.input.LEFT.is_pressed or self.input.RIGHT.is_pressed:
            self.state = self.state_initial_dash

    def allow_crouch(self):
        if self.input.DOWN:
            self.state = self.state_crouch

    def allow_aerial_drift(self):
        if self.input.LEFT:
            self.u -= self.acceleration_to_apply(-self.u, self.air_acceleration, self.air_speed)
        if self.input.RIGHT:
            self.u += self.acceleration_to_apply(self.u, self.air_acceleration, self.air_speed)

    def allow_aerial_up_b(self):
        if self.input.B.is_pressed and self.input.UP:
            self.do_move(self.AerialUpB)

    def landing_lag(self, ticks):
        def func():
            self.image = self.sprites["crouch_" + self.facing].loop(self.animation_frame)
            if (self.tick == ticks) or (ticks == 0):
                self.state = self.state_stand

        return func

    def enforce_max_fall_speed(self):
        if self.v > 0 and abs(self.v) > self.fall_speed:
            self.v = self.fall_speed

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

        self.update_image(frame_data)
        self.update_hitboxes(frame_data)
        self.handle_physics()

    def handle_physics(self):
        """ handle grounded physics by default"""
        self.character.grounded_physics()

    def update_image(self, frame_data):
        image = frame_data.get("image")
        if image:
            self.character.image = image

    def update_hitboxes(self, frame_data):
        active_hitboxes = frame_data.get("hitboxes", [])
        self.character.level.add_hitbox(*active_hitboxes)

    def get_next_state(self):
        """ This needs to be a method because we might need to instantiate a class-based state. """
        return self.character.state_stand

    def end(self):
        self.character.state = self.get_next_state()
        return self.character.state()  # execute the state


class AerialMove(Move):
    landing_lag: int

    def handle_physics(self):
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

    def get_next_state(self):
        return self.character.state_fall

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
                character.input.DOWN and character.state == character.state_fall
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
