from collections import namedtuple

import numpy as np
import pygame

from numpy import sign

Point = namedtuple("Point", ["x", "y"])

# key mapping -- todo: make a better class for this and make Entity (or a mixin)
#  receive a keymap parameter.
class Keys:
    JUMP = pygame.K_UP
    LEFT = pygame.K_LEFT
    RIGHT = pygame.K_RIGHT
    UP = pygame.K_UP
    DOWN = pygame.K_DOWN
    FIRE = pygame.K_SPACE

class Entity(pygame.sprite.Sprite):
    """This is the class from which all game objects will be derived---Characters,
    projectiles, platforms, etc.

    This class has
    - self.rect (centered on self.xy)
    - self.image
    - self.draw()
    which are used by all subclasses.
    """
    debug_color = pygame.Color(69, 69, 69)
    debug_background = pygame.Color(255, 255, 255)

    def __init__(self, x, y, width, height, color=None, groups=[]):
        super().__init__(*groups)

        self.font = pygame.font.Font(
            pygame.font.match_font("ubuntucondensed"),
            12,
        )
        self.color = color if color else self.debug_color
        self.width = width  # todo: give these more specific names e.g. collision_width
        self.height = height
        self.state = None
        # rect is used for simple collisions
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = x, y

    # =============== properties ====================
    # x and y default to the center of self.rect

    @property
    def x(self):
        return self.rect.center[0]

    @x.setter
    def x(self, new_x):
        self.rect.center = new_x, self.rect.center[1]

    @property
    def y(self):
        return self.rect.center[1]

    @y.setter
    def y(self, new_y):
        self.rect.center = self.rect.center[0], new_y

    @property
    def centroid(self):
        return Point(*self.rect.center)

    @property
    def xy(self):
        """In case this is different from centroid in a subclass"""
        return Point(self.x, self.y)

    # ============= drawing functions ==============

    def align_image_rect(self):
        """
        self.image_rect is used to display self.image (in much the same way the default
        Group.draw() uses Sprite.rect) Default: center self.image on the center of
        self.rect
        """
        # get rect with the same dimensions as self.image
        self.image_rect = self.image.get_rect()
        # center it on self.rect.center
        self.image_rect.center = self.rect.center

    def draw_image(self, surface):
        """This is pretty general, and doesn't have to be an animated image, so I am
        leaving it attached to the Entity class, not the AnimationMixin."""
        if self.image:
            self.align_image_rect()
            surface.blit(self.image, self.image_rect)

    def draw_debug(self, surface):
        # draw self.rect
        pygame.draw.rect(surface, self.debug_color, self.rect, 1)
        # draw centroid
        centroid_width = 10
        centroid = pygame.Rect(0, 0, centroid_width, centroid_width)
        centroid.center = self.centroid
        pygame.draw.ellipse(surface, self.debug_color, centroid, 1)
        text = self.font.render("CENTROID", True, self.debug_color,
                                self.debug_background)
        textRect = text.get_rect()
        textRect.midtop = self.centroid
        surface.blit(text, textRect)
        # draw XY
        xy_width = 10
        xy = pygame.Rect(0, 0, xy_width, xy_width)
        xy.center = self.xy
        pygame.draw.ellipse(surface, self.debug_color, xy, 1)
        text = self.font.render("XY", True, self.debug_color,
                                self.debug_background)
        textRect = text.get_rect()
        textRect.midbottom = self.xy
        surface.blit(text, textRect)
        # draw sprite bounding box
        if self.image:
            pygame.draw.rect(surface, self.debug_color, self.image_rect, 1)

    def draw(self, surface, debug=False):
        self.draw_image(surface)
        if debug:
            self.draw_debug(surface)

    def update(self, keys):
        """Subclasses should extend this function"""
        pass

    def debug_print(self):
        print(
            f"x = {self.x}",
            f"y = {self.y}",
        )


class Platform(Entity):
    image = None

    def __init__(self, x, y, width, height, can_fall_through=True, **kwargs):
        super().__init__(x=x, y=y, width=width, height=height, **kwargs)
        self.can_fall_through = can_fall_through
        # override default Entity rect placement
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height))
        self.image.fill(self.color)

    @property
    def color(self):
        return (0, 255, 0) if self.can_fall_through else (255, 0, 0)

    @color.setter
    def color(self, *args, **kwargs):
        """Don't allow setting color"""
        pass


class AnimationMixin:
    """Handles animation for a state machine class. Subclasses should have their own
    dictionary of sprite animations. Each state function can then use `frames_elapsed`
    counter to assign the correct sprite frame to self.image"""
    frames_elapsed = 0

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        """Reset animation counter when state changes"""
        self._state = new_state
        self.frames_elapsed = 0

    def update_animation(self):
        """Call this inside subclass update method"""
        self.frames_elapsed += 1


class PhysicsMixin:
    """Introduces velocity and basic physics"""
    # You'll need to implement these parameters in subclasses
    GRAVITY: int
    FALL_SPEED: int
    FRICTION: float
    AIR_RESISTANCE: float
    airborne: bool

    u = 0  # horizontal velocity
    v = 0  # vertical velocity

    def update_physics(self):
        # update position
        self.x += self.u
        self.y += self.v

        # update vertical position
        # if moving downwards faster than fall speed
        if self.v > 0 and abs(self.v) > self.FALL_SPEED:
            pass  # don't apply gravity
        else:  # if moving upwards, or if falling slower than the fall speed
            self.v += self.GRAVITY

        # reduce speeds
        if self.airborne:
            self.u *= (1 - self.AIR_RESISTANCE)  # air resistance
            self.v *= (1 - self.AIR_RESISTANCE)  # air resistance
        else:
            self.u *= (1 - self.FRICTION)  # "friction"
            self.v = 0  # this is the correct place to set this

        # don't allow sub-pixel speeds
        self.u = 0 if abs(self.u) < .5 else self.u
        self.v = 0 if abs(self.v) < .5 else self.v


class CollisionMixin:
    rect: pygame.Rect
    centroid: property

    def collide_solid_platform(self, platform):
        """Move self outside boundaries of solid platform."""
        x_overlap = (min(self.rect.right, platform.rect.right) -
                     max(self.rect.left, platform.rect.left))
        y_overlap = (min(self.rect.bottom, platform.rect.bottom) -
                     max(self.rect.top, platform.rect.top))
        if x_overlap >= y_overlap:
            # move vertically
            # allow a small overlap to stand on a platform and maintain contact
            if y_overlap <= 1 and self.centroid.y < platform.centroid.y:
                return
            # if self is below platform
            if self.centroid.y >= platform.centroid.y:
                # bump head
                self.rect.top = platform.rect.bottom
                self.v = 0
            else:
                self.rect.bottom = platform.rect.top + 1  # keep contact w. platform
        else:
            # move horizontally
            if self.centroid.x >= platform.centroid.x:
                self.rect.left = platform.rect.right
            else:
                self.rect.right = platform.rect.left


class MovingEntity(Entity, AnimationMixin):
    SPEED = 2

    # physics parameters
    GRAVITY = 1
    FRICTION = .5
    AIR_RESISTANCE = .1
    FALL_SPEED = 5
    airborne = False

    # drawing params
    image = pygame.Surface((50, 50))
    image.fill(pygame.color.THECOLORS["goldenrod"])

    def update(self, keys):
        if keys[Keys.RIGHT]:
            self.x += self.SPEED
        if keys[Keys.LEFT]:
            self.x -= self.SPEED
        if keys[Keys.DOWN]:
            self.y += self.SPEED
        if keys[Keys.UP]:
            self.y -= self.SPEED

        self.update_animation()


class Projectile(Entity, AnimationMixin):
    sprites: "spritedict"  # todo: make proper class for this.
    speed: int
    image: pygame.Surface

    def __init__(self, x, y, width, height, groups=[], facing="right"):
        super().__init__(x, y, width, height, groups=groups)
        self.facing = facing

    def update(self, keys):

        if self.facing == "right":
            self.x += self.speed
            self.image = self.sprites["right"].get_frame(self.frames_elapsed)
        elif self.facing == "left":
            self.x -= self.speed
            self.image = self.sprites["left"].get_frame(self.frames_elapsed)
        else:
            raise Exception("invalid `facing` param for Projectile!")

        self.update_animation()


class Character(Entity, AnimationMixin, CollisionMixin):

    # class properties
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
    _friction: float
    air_resistance: float
    crouch_height_multiplier: float

    # drawing
    sprites: dict  # of SpriteAnimations
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
        RUN_LEFT = "RUN_LEFT"
        RUN_RIGHT = "RUN_RIGHT"
        SQUAT = "SQUAT"
        FALL = "FALL"

    # references to other objects
    level = None

    def __init__(self, x, y, groups=[]):

        super().__init__(x, y, self.width, self.height, groups=groups)

        self.u = 0  # todo: move to PhysicsMixin.__init__()
        self.v = 0
        self.state = self.states.FALL
        self.fastfall = False
        self.state_lookup = {
            self.states.STAND: self.state_stand,
            self.states.JUMPSQUAT: self.state_jumpsquat,
            self.states.FALL: self.state_fall,
            self.states.RUN: self.state_run,
            self.states.SQUAT: self.state_squat,
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
    def friction(self):
        if self.state in (self.states.JUMPSQUAT, self.states.SQUAT):
            return -.05
        else:
            return self._friction

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
        platforms = pygame.sprite.spritecollide(self,
                                                self.level.platforms,
                                                dokill=False)
        for platform in platforms:
            # this function handles the physics -- not allowing self to clip through
            # platforms etc.
            if platform.can_fall_through:
                pass
            else:
                self.collide_solid_platform(platform)
            # if the platform is below self, set airborne to False
            if platform.centroid.y > self.centroid.y:
                self.aerial_jumps_used = 0  # reset double jump counter
                self.fastfall = False
                return False
        return True

    # ============== drawing functions ===============

    def align_image_rect(self):
        self.image_rect = self.image.get_rect()
        self.image_rect.midbottom = self.rect.midbottom

    # ============== main methods ====================

    def update(self, keys):
        self.keys = keys
        self.execute_state()
        self.update_physics()
        self.enforce_screen_limits()
        # self.debug_print()
        self.update_cooldowns()
        self.update_animation()

    def update_cooldowns(self):
        # todo: make a cooldowns mixin which does this for a list of cooldowns.
        if self.double_jump_cooldown:
            self.double_jump_cooldown -= 1

    def execute_state(self):
        """Each state has a corresponding function that handles keypresses and events"""
        func = self.state_lookup[self.state]  # grab the state function
        func()  # execute it

    def update_physics(self):
        # always apply gravity. Other functions can enforce max fall speed
        self.v += self.gravity

        # reduce speeds
        if self.airborne:  # air resistance
            self.u *= (1 - self.air_resistance)
        else:  # friction
            self.u *= (1 - self.friction)
            self.v = 0

        # don't allow sub-pixel horizontal speeds. This prevents infinite sliding to
        # the left
        self.u = 0 if abs(self.u) < 0.2 else self.u

        # update position
        self.x += self.u
        self.y += self.v

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
        if self.keys[Keys.DOWN] and self.v > 0:
            self.fastfall = True
            self.v = self.fall_speed

    # ========================= state functions ================================

    def state_stand(self):
        self.image = self.sprites["stand"].get_frame(self.frames_elapsed)
        if self.keys[Keys.JUMP]:  # enter jumpsquat
            self.state = self.states.JUMPSQUAT
        if self.keys[Keys.DOWN]:  # enter squat
            self.state = self.states.SQUAT
        if self.keys[Keys.LEFT] or self.keys[Keys.RIGHT]:
            self.state = self.states.RUN
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.states.FALL

    def state_jumpsquat(self):
        self.image = self.sprites["crouch"].get_frame(self.frames_elapsed)
        if self.frames_elapsed == self.jumpsquat_frames:
            self.enter_jump()
        # todo: add any other actions that are allowed in jumpsquat state... wavedash ahem.

    def enter_jump(self):
        self.v = -self.jump_power
        self.y -= 1  # need this to become airborne. Hacky?
        self.state = self.states.FALL
        self.fastfall = False

    def state_fall(self):
        # sprite selection
        f = self.frames_elapsed
        limit = 2  # fixme: don't hard-code this here
        if self.v > 0:
            if abs(self.u) < limit:
                self.image = self.sprites["fall"].get_frame(f)
            elif self.u > 0:
                self.image = self.sprites["fall_right"].get_frame(f)
            else:
                self.image = self.sprites["fall_left"].get_frame(f)
        else:
            if abs(self.u) < limit:
                self.image = self.sprites["jump"].get_frame(f)
            elif self.u > 0:
                self.image = self.sprites["jump_right"].get_frame(f)
            else:
                self.image = self.sprites["jump_left"].get_frame(f)

        # update horizontal position
        if self.keys[Keys.LEFT]:
            self.u -= self.air_acceleration
        if self.keys[Keys.RIGHT]:
            self.u += self.air_acceleration
        if abs(self.u) > self.air_speed:
            self.u = sign(self.u) * self.air_speed

        # double-jump
        if (self.keys[Keys.JUMP] and
                self.aerial_jumps_used < self.aerial_jumps and
                not self.double_jump_cooldown):
            self.double_jump_cooldown = self.double_jump_cooldown_frames
            self.aerial_jumps_used += 1
            self.enter_jump()

        self.enforce_max_fall_speed()
        self.allow_fastfall()

        if not self.airborne:
            self.state = self.states.STAND
            self.v = 0

    def state_squat(self):
        self.image = self.sprites["crouch"].get_frame(self.frames_elapsed)
        if self.airborne:
            self.state = self.states.FALL
        if self.keys[Keys.JUMP]:
            self.state = self.states.JUMPSQUAT
        # if squat key released, exit squat state
        if not self.keys[Keys.DOWN]:
            self.state = self.states.STAND

    def state_run(self):
        # sprite selection
        if self.u > 0:
            self.image = self.sprites["run_right"].get_frame(
                self.frames_elapsed)
        else:
            self.image = self.sprites["run_left"].get_frame(self.frames_elapsed)

        if not self.keys[Keys.LEFT] and not self.keys[Keys.RIGHT]:
            self.state = self.states.STAND
        if self.keys[Keys.LEFT]:
            self.u -= self.ground_acceleration
        if self.keys[Keys.RIGHT]:
            self.u += self.ground_acceleration
        if abs(self.u) > self.ground_speed:  # enforce run speed
            self.u = sign(self.u) * self.ground_speed
        if self.keys[Keys.JUMP]:
            self.state = self.states.JUMPSQUAT
        if self.keys[Keys.DOWN]:
            self.state = self.states.SQUAT
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.states.FALL


