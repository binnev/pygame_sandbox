from collections import namedtuple

import pygame

from platformer import states
from platformer.conf import SCREEN_WIDTH, SCREEN_HEIGHT, Keys
"""
Try shapely: https://shapely.readthedocs.io/en/latest/manual.html
For intersections of hitboxes, hurtboxes, etc
"""


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


def sign(number):
    # todo: this will not work correctly for zero...
    return 1 if number > 0 else -1


def screen_y(y):
    return SCREEN_HEIGHT - y


class Sprite:

    def __init__(self, frames: list):
        self.frames = frames

    def get_frame(self, index):
        return self.frames[index % len(self.frames)]


Point = namedtuple("Point", ["x", "y"])


class Platform(pygame.sprite.Sprite):

    def __init__(self, rect_args, can_fall_through=True, groups=[], **kwargs):
        self.rect = pygame.Rect(*rect_args, **kwargs)
        self.can_fall_through = can_fall_through
        super().__init__(*groups)

    def draw(self, window):
        pygame.draw.rect(window, self.color, self.rect, 1)

    @property
    def color(self):
        return (0, 255, 0) if self.can_fall_through else (255, 0, 0)


class Entity(pygame.sprite.Sprite):
    speed = 2

    # Constructor. Pass in the color of the block,
    # and its x and y position
    def __init__(self,
                 color,
                 x,
                 y,
                 width,
                 height,
                 canvas_width=None,
                 canvas_height=None,
                 groups=[]):
        self.font = pygame.font.Font(pygame.font.match_font("ubuntucondensed"),
                                     12)
        self.x = x
        self.y = y
        self.color = color
        self.width = width  # todo: give these more specific names e.g. collision_width
        self.height = height
        self.canvas_width = canvas_width if canvas_width else width * 2
        self.canvas_height = canvas_height if canvas_height else height * 2
        self.canvas = pygame.Surface([self.canvas_width, self.canvas_height])
        self.canvas.fill((0, 0, 0, 0))
        # fixme: don't use this rect for collisions
        self.rect = self.canvas.get_rect()
        self.rect.center = (self.x, self.y)
        # fixme: move this rect to self.x, y in here.

        # Call the parent class (Sprite) constructor
        super().__init__(*groups)

    @property
    def centroid(self):
        return self.x, self.y

    @property
    def image(self):
        # todo: split this up into multiple functions that subclasses can edit
        # ================== image ==================
        # todo: this isn't always going to be a rectangle!
        pygame.draw.rect(self.canvas, self.color, (
            self.canvas_width/2-self.width/2,
            self.canvas_height/2-self.height/2,
            self.width, self.height))

        # ================== debugging ==================
        canvas_rect = self.canvas.get_rect()
        # bounding box of the canvas (the canvas onto which the sprites, hurt/hitboxes,
        # etc are drawn)
        pygame.draw.rect(self.canvas, self.color, canvas_rect, 1)
        # centroid
        centroid_width = 5
        pygame.draw.rect(self.canvas, (255, 0, 0), (
            canvas_rect.width / 2 - centroid_width / 2,
            canvas_rect.height / 2 - centroid_width / 2,
            centroid_width,
            centroid_width,
        ), 1)
        text = self.font.render("CENTROID", True, (255, 255, 255), None)
        textRect = text.get_rect()
        textRect.midbottom = canvas_rect.width / 2, canvas_rect.height / 2
        self.canvas.blit(text, textRect)
        # # base
        # pygame.draw.rect(self.canvas, (0, 255, 0), (
        #     canvas_rect.width / 2 - centroid_width / 2,
        #     canvas_rect.height - centroid_width / 2,
        #     centroid_width,
        #     centroid_width,
        # ), 1)
        # text = self.font.render("BASE", True, (255, 255, 255), None)
        # textRect = text.get_rect()
        # textRect.midbottom = canvas_rect.width/2, canvas_rect.height
        # self.canvas.blit(text, textRect)

        return self.canvas

    def update(self, keys):
        if keys[Keys.DOWN]:
            self.y += self.speed
        if keys[Keys.UP]:
            self.y -= self.speed
        if keys[Keys.RIGHT]:
            self.x += self.speed
        if keys[Keys.LEFT]:
            self.x -= self.speed
        self.debug_print()
        self.rect.center = (self.x, self.y)  # fixme

    def debug_print(self):
        print(
            f"x = {self.x}",
            f"y = {self.y}",
        )


class Thing(pygame.sprite.Sprite):
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
            Sprite([pygame.image.load("sprites/stand.png")]),
        states.SQUAT:
            Sprite([pygame.image.load("sprites/squat.png")]),
        states.JUMPSQUAT:
            Sprite([pygame.image.load("sprites/squat.png")]),
        states.FALL:
            Sprite([pygame.image.load("sprites/jump.png")]),
        states.RUN:
            Sprite([
                pygame.image.load("sprites/walk_right_1.png"),
                pygame.image.load("sprites/walk_right_2.png"),
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
