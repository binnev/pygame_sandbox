from collections import namedtuple

import pygame

from platformer import states
from platformer.conf import SCREEN_WIDTH, SCREEN_HEIGHT, Keys
from platformer.sprites import SpriteGroup, PROJECTILE_SPRITES, BLOB_SPRITES
from platformer.utils import sign

Point = namedtuple("Point", ["x", "y"])


class Level(SpriteGroup):
    # sprite groups
    platforms = SpriteGroup()
    characters = SpriteGroup()
    projectiles = SpriteGroup()

    def add_objects(self, *objects, type=None):
        # add to Level spritegroup (similar to "all" group)
        self.add(*objects)

        # todo: allow multiple types?
        if type == "platform":
            self.platforms.add(*objects)
        if type == "character":
            self.characters.add(*objects)
        if type == "projectile":
            self.projectiles.add(*objects)
        # give the object a reference to this level
        for obj in objects:
            obj.level = self


class Entity(pygame.sprite.Sprite):
    """This is the class from which all game objects will be derived---Characters,
    projectiles, platforms, etc. """

    def __init__(self, x, y, width, height, color=None, groups=[]):
        super().__init__(*groups)

        self.font = pygame.font.Font(pygame.font.match_font("ubuntucondensed"),
                                     12)
        self.x = x
        self.y = y
        self.color = color if color else (69, 69, 69)
        self.width = width  # todo: give these more specific names e.g. collision_width
        self.height = height
        self.state = None
        # rect is used for simple collision detection e.g. with platforms
        # it is also used to draw the sprite
        self._rect = pygame.Rect(0, 0, self.width, self.height)
        self.update_rect_position()
        self.sprite = None  # subclasses can overwrite this

    @property
    def rect(self):
        return self._rect

    @property
    def centroid(self):
        return Point(self.x, self.y)

    # ============= drawing functions ==============

    def draw_sprite(self, surface):
        # todo: the rect argument here gives the position at which to blit. The top left
        #  corner of the rect is taken as the position to blit. The size of the rect doesn't
        #  affect the blitting. So make sure that top left corner is in the right place!
        if self.sprite:
            surface.blit(self.sprite, self.rect)

    def draw_debug(self, surface):
        # bounding box
        pygame.draw.rect(surface, self.color, self.rect, 1)
        # centroid
        centroid_width = 10
        centroid = pygame.Rect(0, 0, centroid_width, centroid_width)
        centroid.center = self.centroid
        pygame.draw.ellipse(surface, self.color, centroid, 1)
        text = self.font.render("CENTROID", True, (255, 255, 255), None)
        textRect = text.get_rect()
        textRect.midbottom = self.centroid
        surface.blit(text, textRect)

    def draw(self, surface, debug=False):
        self.draw_sprite(surface)
        if debug:
            self.draw_debug(surface)

    def update(self, keys):
        """Subclasses should extend this function"""
        self.update_rect_position()  # this makes sprite follow object

    def update_rect_position(self):
        """Subclasses can overwrite this"""
        self._rect.center = self.centroid

    def debug_print(self):
        print(
            f"x = {self.x}",
            f"y = {self.y}",
        )


class Platform(Entity):

    def __init__(self, x, y, width, height, can_fall_through=True, **kwargs):
        self.can_fall_through = can_fall_through
        super().__init__(x=x, y=y, width=width, height=height, **kwargs)

    def update_rect_position(self):
        self._rect.topleft = self.centroid

    @property
    def color(self):
        return (0, 255, 0) if self.can_fall_through else (255, 0, 0)

    @color.setter
    def color(self, *args, **kwargs):
        pass


class Projectile(Entity):
    speed = 9
    sprites = PROJECTILE_SPRITES

    def __init__(self,
                 x,
                 y,
                 width,
                 height,
                 color=None,
                 groups=[],
                 facing="right"):
        super().__init__(x, y, width, height, color, groups)
        self.frames_elapsed = 0  # todo: make a mixin for this
        self.facing = facing

    def update(self, keys):
        super().update(keys)  # always do this

        if self.facing == "right":
            self.x += self.speed
            self.sprite = self.sprites["right"].get_frame(self.frames_elapsed)
        elif self.facing == "left":
            self.x -= self.speed
            self.sprite = self.sprites["left"].get_frame(self.frames_elapsed)
        else:
            raise Exception("invalid `facing` param for Projectile!")
        self.frames_elapsed += 1


class Character(Entity):
    sprites = BLOB_SPRITES

    # class properties (constants)
    width = 100
    height = 100
    ground_acceleration = 10
    ground_speed = 7
    air_acceleration = 2
    air_speed = 6
    fall_acceleration = 2
    _fall_speed = 5
    fastfall_multiplier = 2.5
    aerial_jumps = 3
    jump_power = 20
    jumpsquat_frames = 10
    aerial_jumpsquat_frames = 1
    _friction = 0.1
    air_resistance = 0.05

    # put these in a subclass
    PROJECTILE_COOLDOWN = 15

    def __init__(self, x, y, groups=[]):

        super().__init__(x, y, self.width, self.height, color=None, groups=groups)

        self.level = None
        self.u = 0
        self.v = 0
        self.state = states.FALL
        self.previous_state = self.state
        self.fastfall = False
        self.state_lookup = {
            states.STAND: self.state_stand,
            states.JUMPSQUAT: self.state_jumpsquat,
            states.FALL: self.state_fall,
            states.RUN: self.state_run,
            states.SQUAT: self.state_squat,
        }
        self.aerial_jumps_used = 0
        self.frames_elapsed = 0
        self.font = pygame.font.Font("freesansbold.ttf", 10)

        # put these in a subclass
        self.projectile_cooldown = 0

    # ============== properties ==============

    @property
    def friction(self):
        if self.state in (states.JUMPSQUAT, states.SQUAT):
            return self._friction / 10
        else:
            return self._friction

    @property
    def fall_speed(self):
        if self.fastfall:
            return self._fall_speed * self.fastfall_multiplier
        else:
            return self._fall_speed

    @property
    def centroid(self):
        # todo: replace this with auto calculation centroid from sprite
        return Point(self.x, self.y - self.height / 2)

    @property
    def base(self):
        return Point(*self.rect.midbottom)

    @property
    def airborne(self):
        # todo: optimise this logic
        # todo: replace this with pygame built in rect collisions
        # todo: add in clause to only land on platforms when moving downwards
        # todo: prevent clipping through solid platforms. Should go somewhere else really.
        for platform in self.level.platforms:
            # is self within the horizontal bounds of the platform
            # and is self.base.y within a few pixels of the top of the platform?
            # then we're standing on the platform.
            if (platform.rect.left <= self.x <= platform.rect.right and
                    platform.rect.top - 3 <= self.base.y <=
                    platform.rect.top + 3 and self.v >= 0  # moving downwards
               ):
                # if the platform is drop-through-able and the down key is pressed
                if platform.can_fall_through and self.keys[Keys.DOWN]:
                    return True
                else:
                    self.aerial_jumps_used = 0  # reset double jump counter
                    return False
        return True

    # ============== main methods ====================

    def update(self, keys):
        self.keys = keys
        self.previous_state = self.state
        self.handle_state()  # respond to keypresses first
        if self.state != self.previous_state:
            self.frames_elapsed = 0
        self.handle_physics()
        self.update_rect_position()
        self.enforce_screen_limits()
        self.debug_print()
        # todo: move to states
        if keys[Keys.FIRE] and not self.projectile_cooldown:
            self.create_projectile()
            self.projectile_cooldown = self.PROJECTILE_COOLDOWN
        self.update_cooldowns()
        self.frames_elapsed += 1

    def handle_state(self):
        """Each state has a corresponding function that handles keypresses and events"""
        func = self.state_lookup[self.state]
        func()

    def handle_physics(self):
        # update position
        self.x += self.u
        self.y += self.v

        # reduce horizontal speeds
        if self.airborne:
            self.u *= (1 - self.air_resistance)  # air resistance
        else:
            self.u *= (1 - self.friction)  # "friction"

    def enforce_screen_limits(self):
        if self.x < 0:
            self.x = 0
            self.u = 0
        if self.x > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH
            self.u = 0
        if self.y < 0:
            self.y = 0
            self.v = 0
        if self.y > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT
            self.v = 0
            self.state = states.STAND

    def debug_print(self):
        print(
            f"state = {self.state},",
            f"airborne = {self.airborne},",
            f"x = {self.x:.2f},",
            f"y = {self.y:.2f},",
            f"base.y = {self.base.y:.2f},",
            f"u = {self.u:.2f},",
            f"v = {self.v:.2f},",
            f"friction = {self.friction:.2f},",
            f"aerial_jumps_used = {self.aerial_jumps_used}",
            f"frames_elapsed = {self.frames_elapsed}",
        )

    def update_cooldowns(self):
        if self.projectile_cooldown > 0:
            self.projectile_cooldown -= 1

    # ========================= state functions ================================

    def state_stand(self):
        self.sprite = self.sprites["stand"].get_frame(self.frames_elapsed)
        if self.keys[Keys.JUMP]:  # enter jumpsquat
            self.enter_jumpsquat()
        if self.keys[Keys.DOWN]:  # enter squat
            self.state = states.SQUAT
        if self.keys[Keys.LEFT] or self.keys[Keys.RIGHT]:
            self.state = states.RUN
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = states.FALL

    def enter_jumpsquat(self):
        self.state = states.JUMPSQUAT

    def state_jumpsquat(self):
        self.sprite = self.sprites["crouch"].get_frame(self.frames_elapsed)
        # if end of jumpsquat reached, begin jump
        if self.airborne:
            if self.aerial_jumps_used < self.aerial_jumps:
                if self.frames_elapsed >= self.aerial_jumpsquat_frames:
                    self.enter_jump()
            else:
                self.state = states.FALL
        else:
            if self.frames_elapsed == self.jumpsquat_frames:
                self.enter_jump()
        # todo: add any other actions that are allowed in jumpsquat state... wavedash ahem.

    def enter_jump(self):
        self.v = -self.jump_power
        self.state = states.FALL
        self.fastfall = False

    def state_fall(self):
        # sprite selection
        f = self.frames_elapsed
        limit = 2
        if self.v > 0:
            if abs(self.u) < limit:  # fixme: don't hard-code this
                # self.sprite = self.sprites["fall"].get_frame(f)
                pass
            elif self.u > 0:
                # self.sprite = self.sprites["fall_right"].get_frame(f)
                pass
            else:
                # self.sprite = self.sprites["fall_left"].get_frame(f)
                pass
        else:
            if abs(self.u) < limit:
                self.sprite = self.sprites["jump"].get_frame(f)
                pass
            elif self.u > 0:
                # self.sprite = self.sprites["jump_right"].get_frame(f)
                pass
            else:
                # self.sprite = self.sprites["jump_left"].get_frame(f)
                pass

        # update vertical position
        # if moving downwards faster than fall speed
        if self.v > 0 and abs(self.v) > self.fall_speed:
            pass  # don't apply gravity
        else:  # if moving upwards, or if falling slower than the fall speed
            self.v += self.fall_acceleration

        # update horizontal position
        if self.keys[Keys.LEFT]:
            self.u -= self.air_acceleration
        if self.keys[Keys.RIGHT]:
            self.u += self.air_acceleration
        if abs(self.u) > self.air_speed:
            self.u = sign(self.u) * self.air_speed

        # double-jump todo: time limit on repeated double jumps
        if (self.keys[Keys.JUMP] and
                self.aerial_jumps_used < self.aerial_jumps and
                self.frames_elapsed > 10):  # fixme don't hard-code this stuff
            self.enter_jumpsquat()
            self.aerial_jumps_used += 1

        # fastfall if moving downwards
        if self.keys[Keys.DOWN] and self.v > 0:
            self.fastfall = True
            self.v = self.fall_speed

        if not self.airborne:
            self.state = states.STAND
            self.v = 0

    def state_squat(self):
        self.sprite = self.sprites["crouch"].get_frame(self.frames_elapsed)
        if self.airborne:
            self.state = states.FALL
        if self.keys[Keys.JUMP]:
            self.enter_jumpsquat()
        # if squat key released, exit squat state
        if not self.keys[Keys.DOWN]:
            self.state = states.STAND

    def state_run(self):
        # sprite selection
        if self.u > 0:
            self.sprite = self.sprites["run_right"].get_frame(
                self.frames_elapsed)
        else:
            self.sprite = self.sprites["run_left"].get_frame(
                self.frames_elapsed)

        if not self.keys[Keys.LEFT] and not self.keys[Keys.RIGHT]:
            self.state = states.STAND
        if self.keys[Keys.LEFT]:
            self.u -= self.ground_acceleration
        if self.keys[Keys.RIGHT]:
            self.u += self.ground_acceleration
        if abs(self.u) > self.ground_speed:  # enforce run speed
            self.u = sign(self.u) * self.ground_speed
        if self.keys[Keys.JUMP]:
            self.enter_jumpsquat()
        if self.keys[Keys.DOWN]:
            self.state = states.SQUAT
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = states.FALL

    # ============ actions ==============

    def create_projectile(self):
        facing = "right" if self.u > 0 else "left"
        self.level.add_objects(Projectile(*self.centroid, 100, 100,
                                          facing=facing))


class Blob(Character):
    width = 40
    height = 60
    ground_acceleration = 10
    ground_speed = 7
    air_acceleration = 2
    air_speed = 6
    fall_acceleration = 2
    _fall_speed = 5
    fastfall_multiplier = 2.5
    aerial_jumps = 3
    jump_power = 20
    jumpsquat_frames = 4
    aerial_jumpsquat_frames = 1
    _friction = 0.1
    air_resistance = 0.05
