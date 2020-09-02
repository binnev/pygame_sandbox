from collections import namedtuple
from copy import copy

import numpy
import pygame
from numpy import sign

from base.animation import SpriteAnimation
from base.groups import EntityGroup
from base.keyhandler import KeyHandler
from base.objects.mixins import HistoryMixin, AnimationMixin, CollisionMixin
from base.utils import touching, mask_to_surface, ticks_to_frames, draw_arrow

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

        # fixme: it's stupid to load the font here. Attach this to game or something?
        self.font = pygame.font.Font(pygame.font.match_font("ubuntucondensed"), 12,)
        self.color = color if color else self.debug_color
        self.width = width
        self.height = height
        self.state = None
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.x = x
        self.y = y

    # =============== properties ====================

    @property
    def game(self):
        return self.level.game

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
    def velocity(self):
        return [self.u, self.v]

    @velocity.setter
    def velocity(self, new_velocity):
        self.u, self.v = new_velocity

    @property
    def touchbox(self):
        return self.rect.inflate(self.touchbox_margin, self.touchbox_margin)

    @property
    def mask(self):
        return pygame.mask.from_surface(self.image) if self.image else None

    @property
    def image_rect(self):
        if not hasattr(self, "_image_rect"):
            self._image_rect = self.image.get_rect()
        return self._image_rect

    # ============= drawing functions ==============

    def align_image_rect(self):
        """
        self.image_rect is used to display self.image (in much the same way the default
        Group.draw() uses Sprite.rect) Default: center self.image on the center of
        self.rect
        """
        # center it on self.rect.center
        self.image_rect.center = self.rect.center

    def draw_image(self, surface):
        """This is pretty general, and doesn't have to be an animated image, so I am
        leaving it attached to the Entity class, not the AnimationMixin."""
        if self.image:
            self.align_image_rect()
            surface.blit(self.image, self.image_rect)

    def draw_debug(self, surface):
        if self.image:
            self.align_image_rect()

        # draw self.rect
        pygame.draw.rect(surface, self.debug_color, self.rect, 1)

        # draw object type
        text = self.font.render(self.__class__.__name__, True, self.debug_color)
        textRect = text.get_rect()
        textRect.midbottom = self.rect.midtop
        surface.blit(text, textRect)

        # draw self.touchbox
        pygame.draw.rect(surface, pygame.color.THECOLORS["goldenrod"], self.touchbox, 1)

        # draw self.mask
        if self.mask and self.mask.count():  # if mask not empty
            color = self.debug_color  # pygame.color.THECOLORS["magenta"]
            translucent_color = color[:3] + (50,)
            mask_surface = mask_to_surface(self.mask, translucent_color)
            mask_outline = self.mask.outline()
            # add the outline to the mask surface
            pygame.draw.polygon(mask_surface, color, mask_outline, 1)
            surface.blit(mask_surface, self.image_rect)

        # draw centroid
        centroid_width = 10
        centroid = pygame.Rect(0, 0, centroid_width, centroid_width)
        centroid.center = self.centroid
        pygame.draw.ellipse(surface, self.debug_color, centroid, 1)
        text = self.font.render("CENTROID", True, self.debug_color, self.debug_background)
        textRect = text.get_rect()
        textRect.midtop = self.centroid
        surface.blit(text, textRect)

        # draw XY
        xy_width = 10
        xy = pygame.Rect(0, 0, xy_width, xy_width)
        xy.center = self.xy
        pygame.draw.ellipse(surface, self.debug_color, xy, 1)
        text = self.font.render("XY", True, self.debug_color, self.debug_background)
        textRect = text.get_rect()
        textRect.midbottom = self.xy
        surface.blit(text, textRect)

        # draw sprite bounding box
        if self.image:
            pygame.draw.rect(surface, pygame.color.THECOLORS["lightgray"], self.image_rect, 1)

    def draw(self, surface, debug=False):
        self.draw_image(surface)
        if debug:
            self.draw_debug(surface)

    # ========== other functions =============

    def update(self):
        """Subclasses should extend this function"""
        pass

    def is_touching(self, entity) -> bool:
        if touching(self, entity):
            return True

    # ============ utility functions ===========

    def debug_print(self):
        print(
            f"x = {self.x}", f"y = {self.y}",
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


class MovingEntity(Entity, CollisionMixin, HistoryMixin):
    SPEED = 2

    # default image
    image = pygame.Surface((100, 50))
    pygame.draw.ellipse(image, pygame.color.THECOLORS["lightblue"], (0, 0, 100, 50))
    colorkey = image.get_at((0, 0))
    image.set_colorkey(colorkey)
    image = pygame.transform.rotate(image, 30)

    # historymixin
    attributes_to_remember = ["rect", "x", "y"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        HistoryMixin.__init__(self)
        self.active_hitboxes = EntityGroup()

    def update(self):
        if KeyHandler.is_down(Keys.RIGHT):
            self.x += self.SPEED
        if KeyHandler.is_down(Keys.LEFT):
            self.x -= self.SPEED
        if KeyHandler.is_down(Keys.DOWN):
            self.y += self.SPEED
        if KeyHandler.is_down(Keys.UP):
            self.y -= self.SPEED

        if KeyHandler.is_pressed(Keys.FIRE):
            if not hasattr(self, "hitbox"):
                self.hitbox = Hitbox(
                    damage=20,
                    knockback=20,
                    owner=self,
                    angle=45,
                    x_offset=5,
                    y_offset=-40,
                    width=30,
                    height=40,
                )
                self.level.add(self.hitbox, type="hitbox")
            else:
                self.hitbox.kill()
                del self.hitbox

        self.handle_platform_collisions()
        self.handle_touching()
        self.update_history()

    def handle_touching(self):
        platforms = pygame.sprite.spritecollide(
            self, self.level.platforms, dokill=False, collided=touching
        )
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

    def update(self):

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
        self.image_rect.midbottom = self.rect.midbottom

    # ============== main methods ====================

    def update(self):
        self.keys = KeyHandler.get_down()
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
            f"ticks_elapsed = {self.ticks_elapsed}",
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
        if KeyHandler.is_pressed(Keys.JUMP):  # enter jumpsquat
            self.state = self.states.JUMPSQUAT
        if self.keys[Keys.DOWN]:  # enter squat
            self.state = self.states.SQUAT
        if self.keys[Keys.LEFT] or self.keys[Keys.RIGHT]:
            self.state = self.states.RUN
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.states.FALL

    def state_jumpsquat(self):
        self.image = self.sprites["crouch"].get_frame(self.frames_elapsed)
        if self.ticks_elapsed == self.jumpsquat_frames:
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
        if (
            KeyHandler.is_pressed(Keys.JUMP)
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

    def state_squat(self):
        self.image = self.sprites["crouch"].get_frame(self.frames_elapsed)
        if self.airborne:
            self.state = self.states.FALL
        if KeyHandler.is_pressed(Keys.JUMP):
            self.state = self.states.JUMPSQUAT
        # if squat key released, exit squat state
        if not self.keys[Keys.DOWN]:
            self.state = self.states.STAND

    def state_run(self):
        # sprite selection
        if self.u > 0:
            self.image = self.sprites["run_right"].get_frame(self.frames_elapsed)
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
        if KeyHandler.is_pressed(Keys.JUMP):
            self.state = self.states.JUMPSQUAT
        if self.keys[Keys.DOWN]:
            self.state = self.states.SQUAT
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = self.states.FALL


class Hitbox(Entity):

    # fixme: why doesn't this transparency work?
    debug_color = (*pygame.color.THECOLORS["red"][:3], 150)
    owner = None

    def __init__(
        self,
        knockback,
        knockback_angle,
        width,
        height,
        damage=None,
        owner=None,
        angle=0,
        x=0,
        y=0,
        x_offset=0,
        y_offset=0,
        **kwargs,
    ):
        self.owner = owner
        self.damage = damage
        self.knockback = knockback
        self.knockback_angle = knockback_angle
        self.angle = angle
        self.x_offset = x_offset
        self.y_offset = y_offset
        super().__init__(x=x, y=y, width=width, height=height, **kwargs)

        self.image = pygame.Surface((self.width, self.height)).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        pygame.draw.ellipse(self.image, self.debug_color, (0, 0, self.width, self.height))
        colorkey = self.image.get_at((0, 0))
        self.image.set_colorkey(colorkey)
        self.image = pygame.transform.rotate(self.image, self.angle)

    @property
    def rect(self):
        self.align_to_owner()
        return self._rect

    @rect.setter
    def rect(self, new_rect):
        self._rect = new_rect
        self.align_to_owner()

    def align_to_owner(self):
        if self.owner:
            self._rect.center = (
                self.owner.x + self.x_offset,
                self.owner.y + self.y_offset,
            )

    def draw_debug(self, surface):
        self.draw_image(surface)
        if self.angle is not None:
            draw_arrow(surface, self.centroid, self.knockback_angle, color=self.debug_color)

    def draw(self, surface, debug=False):
        # if debug:
        self.draw_debug(surface)

    def flip_x(self):
        new_hitbox = copy(self)
        new_hitbox.knockback_angle = 180 - self.knockback_angle
        new_hitbox.angle = 180 - self.angle
        new_hitbox.x_offset = -self.x_offset
        return new_hitbox


class Move:
    sprite_animation: SpriteAnimation
    hitbox_mapping: dict  # mapping of frame keys to hitbox values
    # fixme: Hitboxes can't be defined without an owner yet. I need this, because I want to
    #  be able to define them abstractly. I want to describe the hitboxes for all Rannos
    #  before they are assigned to an instance of Ranno.
    # todo: make sure this works when facing left!
    # todo: give hitbox a knockback_angle, and make sure THAT works facing left

    def __init__(self, instance):
        self.instance = instance
        self.hitbox_data = self.map_hitboxes(self.hitbox_mapping)

    def __call__(self, n):
        """ This is the equivalent to the function states. Here n is either ticks or frames;
        we're using it to pick up the correct sprite image and hitboxes. """
        self.image = self.sprite_animation.get_frame(n)
        self.active_hitboxes = self.get_active_hitboxes(n)

    @staticmethod
    def map_hitboxes(hitbox_mapping):
        # todo: allow some frames to have no hitboxes. How will I represent that?
        return {
            frame: hitboxes
            for frames, hitboxes in hitbox_mapping.items()
            for frame in ([frames] if isinstance(frames, int) else range(frames[0], frames[-1] + 1))
        }

    def get_active_hitboxes(self, n):
        hitbox_data = self.hitbox_data.get(n, [])
        return [Hitbox(owner=self.instance, **data) for data in hitbox_data]
