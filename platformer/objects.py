from collections import namedtuple
from pathlib import Path

import pygame

from platformer import states
from platformer.conf import SCREEN_WIDTH, SCREEN_HEIGHT, Keys
from platformer.utils import sign

Point = namedtuple("Point", ["x", "y"])


class SpriteGroup(pygame.sprite.Group):

    def draw(self, surface):
        """draw all sprites onto the surface
        Group.draw(surface): return None
        Draws all of the member sprites onto the given surface.
        """
        sprites = self.sprites()
        for sprite in sprites:
            sprite.draw(surface)
        self.lostsprites = []


class SpriteSheet(object):

    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error as message:
            print('Unable to load spritesheet image:', filename)
            raise SystemExit(message)

    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey=None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey=None):
        "Loads multiple images, supply a list of coordinates"
        return [self.image_at(rect, colorkey) for rect in rects]

    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey=None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0] + rect[2] * x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)


class SpriteAnimation:

    def __init__(self,
                 frame_paths: list,
                 flip_horizontal=False,
                 flip_vertical=False):
        # convert to pathlib path
        frame_paths = [Path(path) for path in frame_paths]
        # load frame image
        self.frames = [
            pygame.image.load(path.as_posix()) for path in frame_paths
        ]
        self.frames = [
            pygame.transform.flip(f, flip_horizontal, flip_vertical)
            for f in self.frames
        ]

    def get_frame(self, index):
        return self.frames[index % len(self.frames)]


class Entity(pygame.sprite.Sprite):

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

    def draw(self, surface):
        self.draw_sprite(surface)
        self.draw_debug(surface)

    def update(self, keys):
        """Intended to be overwritten by subclasses"""
        raise NotImplementedError()

    def update_rect_position(self):
        """Subclasses can overwrite this"""
        self._rect.center = self.centroid

    def debug_print(self):
        print(
            f"x = {self.x}",
            f"y = {self.y}",
        )


class Blob(Entity):
    """
    Simple class to try out movement and collision detection. This class has no states. It
    can just move up/down and left/right. It loads a sprite, and has a hurtbox for collisions.
    """
    # ======================= sprite animations =======================
    # yapf:disable
    sprite_folder = Path("sprites/stick_figure/")
    sprites = {"stand": SpriteAnimation([sprite_folder / "stand.png"]),
        "move_down": SpriteAnimation([sprite_folder / "fall_neutral.png"]),
        "move_down_right": SpriteAnimation([sprite_folder / "fall_right.png"]),
        "move_down_left": SpriteAnimation([sprite_folder / "fall_right.png"],
                                          flip_horizontal=True),
        "move_up": SpriteAnimation([sprite_folder / "jump_neutral.png"]),
        "move_up_right": SpriteAnimation([sprite_folder / "jump_right.png"]),
        "move_up_left": SpriteAnimation([sprite_folder / "jump_right.png"],
                                        flip_horizontal=True),
        "move_right": SpriteAnimation([sprite_folder / "run_right1.png",
                                       sprite_folder / "run_right2.png",
                                       sprite_folder / "run_right3.png",
                                       sprite_folder / "run_right4.png",]),
        "move_left": SpriteAnimation([sprite_folder / "run_right1.png",
                                      sprite_folder / "run_right2.png",
                                      sprite_folder / "run_right3.png",
                                      sprite_folder / "run_right4.png",],
                                     flip_horizontal=True),
    }
    # yapf:enable

    # ================ properties =====================
    speed = 4
    frames_elapsed = 0

    @property
    def rect(self):
        """Automatically makes a rect the size of the current sprite"""
        width = self.sprite.get_rect().width if self.sprite else self.width
        height = self.sprite.get_rect().height if self.sprite else self.height
        self._rect = pygame.Rect(0, 0, width, height)
        self.update_rect_position()
        return self._rect

    def update(self, keys):
        self.update_rect_position()
        self.frames_elapsed += 1
        i = self.frames_elapsed

        # simple movement
        if keys[Keys.UP]:
            self.y -= self.speed
        if keys[Keys.DOWN]:
            self.y += self.speed
        if keys[Keys.RIGHT]:
            self.x += self.speed
        if keys[Keys.LEFT]:
            self.x -= self.speed

        # select sprite
        if keys[Keys.UP]:
            if keys[Keys.RIGHT]:
                self.sprite = self.sprites["move_up_right"].get_frame(i)
            elif keys[Keys.LEFT]:
                self.sprite = self.sprites["move_up_left"].get_frame(i)
            else:
                self.sprite = self.sprites["move_up"].get_frame(i)

        elif keys[Keys.DOWN]:
            if keys[Keys.RIGHT]:
                self.sprite = self.sprites["move_down_right"].get_frame(i)
            elif keys[Keys.LEFT]:
                self.sprite = self.sprites["move_down_left"].get_frame(i)
            else:
                self.sprite = self.sprites["move_down"].get_frame(i)

        elif keys[Keys.RIGHT]:
            self.sprite = self.sprites["move_right"].get_frame(i)

        elif keys[Keys.LEFT]:
            self.sprite = self.sprites["move_left"].get_frame(i)

        else:  # no keys pressed
            self.sprite = self.sprites["stand"].get_frame(i)

    def draw_sprite(self, surface):
        if self.sprite:
            surface.blit(self.sprite, self.rect)


class Platform(Entity):

    def __init__(self, x, y, width, height, can_fall_through=True, **kwargs):
        self.can_fall_through = can_fall_through
        super().__init__(x=x, y=y, width=width, height=height, **kwargs)

    def update_rect_position(self):
        """Subclasses can overwrite this"""
        self._rect.topleft = self.centroid

    @property
    def color(self):
        return (0, 255, 0) if self.can_fall_through else (255, 0, 0)

    @color.setter
    def color(self, *args, **kwargs):
        pass

class Character(pygame.sprite.Sprite):
    # class properties (constants)
    width = 40
    height = 60
    ground_acceleration = 10
    ground_speed = 7
    air_acceleration = 2
    air_speed = 6
    fall_acceleration = 2
    _fall_speed = 5
    fastfall_multiplier = 2.5
    aerial_jumps = 2
    jump_power = 20
    jumpsquat_frames = 4
    _friction = 0.1
    air_resistance = 0.05
    ticks_per_frame = 5
    sprites = {
        states.STAND:
            SpriteAnimation(["sprites/stand.png"]),
        states.SQUAT:
            SpriteAnimation(["sprites/squat.png"]),
        states.JUMPSQUAT:
            SpriteAnimation(["sprites/squat.png"]),
        states.FALL:
            SpriteAnimation(["sprites/jump.png"]),
        states.RUN:
            SpriteAnimation([
                "sprites/walk_right_1.png",
                "sprites/walk_right_2.png",
            ]),
    }

    # these are really instance variables...
    state = None
    fastfall = None
    frames_elapsed = None
    jumpsquat_frames_elapsed = None
    aerial_jumps_used = 0

    def __init__(
        self,
        x,
        y,
        height,
        width,
        level,
        groups,
        u=None,
        v=None,
    ):
        self.level = level
        self.x = x
        self.y = y
        self.u = u if u else 0
        self.v = v if v else 0
        self._height = height
        self._width = width
        self.state = states.FALL
        self.fastfall = False
        self.state_lookup = {
            states.STAND: self.state_stand,
            states.JUMPSQUAT: self.state_jumpsquat,
            states.FALL: self.state_fall,
            states.RUN: self.state_run,
            states.SQUAT: self.state_squat,
        }
        self.frames_elapsed = 0
        self.font = pygame.font.Font("freesansbold.ttf", 10)
        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pygame.Surface([width, height])
        self.image.fill(self.color)

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()

        super().__init__(*groups)

    @property
    def color(self):
        # if not actionable
        if self.state in [states.JUMPSQUAT, states.SQUAT]:
            _color = (255, 0, 0)
        else:
            _color = (255, 255, 255)
        return _color

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
    def width(self):
        return self._width

    @property
    def height(self):
        """this is clumsy. Have the jumpsquat state edit the property"""
        if self.state in (states.JUMPSQUAT, states.SQUAT):
            return self._height * 0.8
        return self._height

    def update(self, keys):
        # todo: implement a state watcher that automatically resets frames_elapsed to zero
        #  when object changes state.
        self.keys = keys
        self.handle_state()  # respond to keypresses first
        self.handle_physics()
        self.enforce_screen_limits()
        self.debug_print()
        # self.draw(window)

    def handle_state(self):
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
            f"jumpsquat_frames_elapsed = {self.jumpsquat_frames_elapsed}",
            f"frames_elapsed = {self.frames_elapsed}",
        )

    def draw(self, window):
        # sprite
        sprite = self.sprites.get(self.state)
        # todo: state functions could easily set self.sprite. Then we could have state_run
        #  handle both the left and right running sprites, for example.
        if sprite:
            frame = sprite.get_frame(self.frames_elapsed //
                                     self.ticks_per_frame)
            window.blit(frame, (self.x - frame.get_rect().width / 2,
                                self.y - frame.get_rect().height))
        # bounding box
        pygame.draw.rect(window, self.color, (
            self.x - self.width / 2,
            self.y - self.height,
            self.width,
            self.height,
        ), 1)
        # centroid
        centroid_width = 5
        pygame.draw.rect(window, (255, 0, 0), (
            self.centroid.x - centroid_width / 2,
            self.centroid.y - centroid_width / 2,
            centroid_width,
            centroid_width,
        ), 1)
        text = self.font.render("centroid", True, (255, 255, 255), None)
        textRect = text.get_rect()
        textRect.midleft = self.centroid
        window.blit(text, textRect)
        # base
        pygame.draw.rect(window, (0, 255, 0), (
            self.base.x - centroid_width / 2,
            self.base.y - centroid_width / 2,
            centroid_width,
            centroid_width,
        ), 1)
        text = self.font.render("base", True, (255, 255, 255), None)
        textRect = text.get_rect()
        textRect.midleft = self.base
        window.blit(text, textRect)

    @property
    def centroid(self):
        # todo: replace this with auto calculation centroid from sprite
        return Point(self.x, self.y - self.height / 2)

    @property
    def base(self):
        return Point(self.x, self.y)

    @property
    def airborne(self):
        # todo: optimise this logic
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

    # ========================= state functions ================================

    def state_stand(self):
        if self.keys[Keys.JUMP]:  # enter jumpsquat
            self.enter_jumpsquat()
        if self.keys[Keys.DOWN]:  # enter squat
            self.state = states.SQUAT
        if self.keys[Keys.LEFT] or self.keys[Keys.RIGHT]:
            self.state = states.RUN
            self.frames_elapsed = 0
        if self.airborne:  # e.g. by walking off the edge of a platform
            self.state = states.FALL

    def enter_jumpsquat(self):
        self.state = states.JUMPSQUAT
        self.jumpsquat_frames_elapsed = 0

    def state_jumpsquat(self):
        self.jumpsquat_frames_elapsed += 1
        # if end of jumpsquat reached, begin jump
        if self.jumpsquat_frames_elapsed == self.jumpsquat_frames:
            self.jumpsquat_frames_elapsed = None
            self.enter_jump()
        # todo: add any other actions that are allowed in jumpsquat state... wavedash ahem.

    def enter_jump(self):
        self.v = -self.jump_power
        self.state = states.FALL
        self.fastfall = False
        self.frames_elapsed = 0

    def state_fall(self):
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
            self.enter_jump()
            self.aerial_jumps_used += 1

        # fastfall if moving downwards
        if self.keys[Keys.DOWN] and self.v > 0:
            self.fastfall = True
            self.v = self.fall_speed

        if not self.airborne:
            self.state = states.STAND
            self.v = 0

        self.frames_elapsed += 1

    def state_squat(self):
        if self.keys[Keys.JUMP]:
            self.enter_jumpsquat()
        # if squat key released, exit squat state
        if not self.keys[Keys.DOWN]:
            self.state = states.STAND

    def state_run(self):
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

        self.frames_elapsed += 1  # animate sprite