from collections import namedtuple, deque
from copy import deepcopy
from pathlib import Path

import numpy as np
import pygame

from numpy import sign

from platformer.objects.groups import EntityGroup
from platformer.utils import touching, mask_to_surface

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

    image: pygame.Surface

    debug_color = pygame.Color(69, 69, 69)
    debug_background = pygame.Color(255, 255, 255)
    touchbox_margin = 1

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
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = x, y

    # =============== properties ====================

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

    @property
    def touchbox(self):
        return self.rect.inflate(self.touchbox_margin, self.touchbox_margin)

    @property
    def mask(self):
        return pygame.mask.from_surface(self.image)

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
        # draw self.touchbox
        pygame.draw.rect(surface, pygame.color.THECOLORS["goldenrod"],
                         self.touchbox, 1)
        # draw self.mask
        if self.mask.count():  # if mask not empty
            color = pygame.color.THECOLORS["magenta"]
            translucent_color = color[:3] + (50,)
            mask_surface = mask_to_surface(self.mask, translucent_color)
            mask_outline = self.mask.outline()
            # add the outline to the mask surface
            pygame.draw.polygon(mask_surface, color, mask_outline, 2)
            surface.blit(mask_surface, self.image_rect)
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
            pygame.draw.rect(surface, pygame.color.THECOLORS["lightgray"],
                             self.image_rect, 1)

    def draw(self, surface, debug=False):
        self.draw_image(surface)
        if debug:
            self.draw_debug(surface)

    # ========== other functions =============

    def update(self, keys):
        """Subclasses should extend this function"""
        pass

    def is_touching(self, entity) -> bool:
        if touching(self, entity):
            return True

    # ============ utility functions ===========

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
            self.u *= 1 - self.AIR_RESISTANCE  # air resistance
            self.v *= 1 - self.AIR_RESISTANCE  # air resistance
        else:
            self.u *= 1 - self.FRICTION  # "friction"
            self.v = 0  # this is the correct place to set this

        # don't allow sub-pixel speeds
        self.u = 0 if abs(self.u) < 0.5 else self.u
        self.v = 0 if abs(self.v) < 0.5 else self.v


class HistoryMixin:
    attributes_to_remember: [str]  # names of the attributes to store in history

    def __init__(self):
        self.history = deque(maxlen=5)
        self.update_history()  # prevents empty queue erroring on startup

    def update_history(self):
        self.history.append({
            attr: deepcopy(getattr(self, attr))
            for attr in self.attributes_to_remember
        })


class CollisionMixin:
    """This mixin requires the subclass to have the following attributes to function"""

    rect: pygame.Rect
    centroid: property
    history: deque
    keys: tuple
    is_touching: "method"

    def get_overlap_with_object(self, obj):
        """Get the x and y overlap between self and obj.rect"""
        x_overlap = min(self.rect.right, obj.rect.right) - max(
            self.rect.left, obj.rect.left)
        y_overlap = min(self.rect.bottom, obj.rect.bottom) - max(
            self.rect.top, obj.rect.top)
        return x_overlap, y_overlap

    def can_stand_on_droppable_platform(self, platform):
        was_above_platform = self.history[-1]["rect"].bottom <= platform.rect.top
        not_holding_down = not self.keys[Keys.DOWN]
        return self.is_touching(
            platform) and was_above_platform and not_holding_down

    def can_stand_on_solid_platform(self, platform):
        x_overlap, y_overlap = self.get_overlap_with_object(platform)
        return (self.is_touching(platform) and x_overlap > 0 and
                self.centroid.y < platform.centroid.y)

    def can_stand_on_platform(self, platform):
        if platform.can_fall_through:
            return self.can_stand_on_droppable_platform(platform)
        else:
            return self.can_stand_on_solid_platform(platform)

    def collide_solid_platform(self, platform):
        # todo: rename this. "separate_platform" ? "handle_collision_solid_platform"?
        #  also, this function assumes that platform can't move but self can.
        """Move self outside boundaries of solid platform."""
        x_overlap, y_overlap = self.get_overlap_with_object(platform)
        if x_overlap > y_overlap:
            if self.centroid.y >= platform.centroid.y:
                self.rect.top = platform.rect.bottom
            else:
                self.rect.bottom = platform.rect.top
        else:
            if self.centroid.x >= platform.centroid.x:
                self.rect.left = platform.rect.right
            else:
                self.rect.right = platform.rect.left

    def collide_droppable_platform(self, platform):
        if self.can_stand_on_droppable_platform(platform):
            # allow a small overlap to stand on a platform and maintain contact
            self.rect.bottom = platform.rect.top

    def handle_platform_collisions(self):
        # todo: have objects store this info in an attribute that is calculated once
        #  per tick
        platforms = pygame.sprite.spritecollide(self,
                                                self.level.platforms,
                                                dokill=False)
        for platform in platforms:
            if platform.can_fall_through:
                print("colliding with droppable platform")
                self.collide_droppable_platform(platform)
            else:
                print("colliding with platform")
                self.collide_solid_platform(platform)


class MovingEntity(Entity, CollisionMixin, HistoryMixin):
    SPEED = 2

    # physics parameters
    GRAVITY = 1
    FRICTION = 0.5
    AIR_RESISTANCE = 0.1
    FALL_SPEED = 5
    airborne = False

    # drawing params
    image = pygame.Surface((100, 50))
    pygame.draw.ellipse(image, pygame.color.THECOLORS["lightblue"],
                        (0, 0, 100, 50))
    colorkey = image.get_at((0, 0))
    image.set_colorkey(colorkey)#, pygame.RLEACCEL)
    image = pygame.transform.rotate(image, 30)

    # todo:
    #  - in order to do mask collision, all the Hitbox needs is an image. That image
    #  can just be a surface with an ellipse drawn on it. That's easy to generate. Then
    #  I can do masks and collision. Just don't *draw* the hitboxes, and they won't
    #  appear in game!
    #  - make hitboxes follow their parent object around, and position correctly
    #  relative to them (including left and right facing versions)

    # scale = 5
    # image = pygame.image.load(
    #     Path("sprites/volleyball/volleyball.png").as_posix())
    # image = pygame.transform.scale(
    #     image,
    #     (image.get_rect().width * scale, image.get_rect().height * scale))

    # historymixin
    attributes_to_remember = ["rect", "x", "y"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        HistoryMixin.__init__(self)
        self.active_hitboxes = EntityGroup()

    def update(self, keys):
        self.keys = keys
        if keys[Keys.RIGHT]:
            self.x += self.SPEED
        if keys[Keys.LEFT]:
            self.x -= self.SPEED
        if keys[Keys.DOWN]:
            self.y += self.SPEED
        if keys[Keys.UP]:
            self.y -= self.SPEED

        self.handle_platform_collisions()
        self.handle_touching()
        self.update_history()

    def handle_touching(self):
        platforms = pygame.sprite.spritecollide(self,
                                                self.level.platforms,
                                                dokill=False,
                                                collided=touching)
        for platform in platforms:
            # this function handles the physics -- not allowing self to clip through
            # platforms etc.
            if platform.can_fall_through:
                print("TOUCHING droppable platform")
            else:
                print("TOUCHING platform")


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


class Character(Entity, AnimationMixin, CollisionMixin, HistoryMixin):

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

    # historymixin
    attributes_to_remember = ["rect", "x", "y"]

    def __init__(self, x, y, groups=[]):

        super().__init__(x, y, self.width, self.height, groups=groups)
        HistoryMixin.__init__(self)

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
            return -0.05
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
        for platform in self.level.platforms:
            if self.can_stand_on_platform(platform):
                return False
        return True

    # ============== drawing functions ===============

    def align_image_rect(self):
        self.image_rect = self.image.get_rect()
        self.image_rect.midbottom = self.rect.midbottom

    # ============== main methods ====================

    def update(self, keys):
        self.keys = keys
        self.update_physics()
        self.execute_state()
        self.enforce_screen_limits(*self.level.game.screen_size)
        self.debug_print()
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
        # update position
        self.x += self.u
        self.y += self.v

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
            self.u *= 1 - self.air_resistance
        else:  # friction
            self.u *= 1 - self.friction
            self.v = 0

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
        if self.keys[Keys.DOWN] and self.v > 0:
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


class Hitbox(Entity):

    debug_color = pygame.color.THECOLORS["red"]

    def __init__(self,
                 damage,
                 knockback,
                 owner=None,
                 angle=0,
                 x_offset=0,
                 y_offset=0,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner
        self.damage = damage
        self.knockback = knockback
        self.angle = angle
        self.x_offset = x_offset
        self.y_offset = y_offset

        self.surface = pygame.Surface(self.rect)
        pygame.draw.ellipse(self.surface, self.debug_color,
                            (0, 0, self.width, self.height))
        self.surface = pygame.transform.rotate(self.surface, self.angle)

    @property
    def x(self):
        if self.owner:
            return self.owner.x + self.x_offset

    @x.setter
    def x(self, new_x):
        pass

    @property
    def y(self):
        if self.owner:
            return self.owner.y + self.y_offset

    @y.setter
    def y(self, new_y):
        pass

    def draw_debug(self, surface):
        super().draw_debug()
        # pygame.draw.ellipse(surface, self.debug_color, self.rect)
        surface.blit(self.surface, (0, 0))
