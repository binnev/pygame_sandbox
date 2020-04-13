import pygame

from tutorial import states
from tutorial.conf import SCREEN_WIDTH, SCREEN_HEIGHT, FLOOR_HEIGHT, Keys
"""
Try shapely: https://shapely.readthedocs.io/en/latest/manual.html
For intersections of hitboxes, hurtboxes, etc
"""


def sign(number):
    return 1 if number > 0 else -1


class Thing:
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
    jump_power = 40
    jumpsquat_frames = 4
    _friction = 0.1
    air_resistance = 0.05

    # these are really instance variables...
    state = None
    fastfall = None
    jumpsquat_frames_elapsed = None

    def __init__(self, x, y, height, width, u=None, v=None):
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

    def update(self, keys, window):
        self.handle_state(keys)  # respond to keypresses first
        self.handle_physics()
        self.enforce_screen_limits()
        self.debug_print()
        self.draw(window)

    def handle_state(self, keys):
        func = self.state_lookup[self.state]
        func(keys)

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
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            self.u = 0
        if self.y < 0:
            self.y = 0
            self.v = 0
        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.v = 0

    def debug_print(self):
        print(
            f"state = {self.state},",
            f"airborne = {self.airborne},",
            f"x = {self.x:.2f},",
            f"y = {self.y:.2f},",
            f"u = {self.u:.2f},",
            f"v = {self.v:.2f},",
            f"friction = {self.friction:.2f},",
            f"jumpsquat_frames_elapsed = {self.jumpsquat_frames_elapsed}",
        )

    def draw(self, window):
        pygame.draw.rect(window, self.color,
                         (self.x, self.y, self.width, self.height))

    @property
    def airborne(self):
        # todo: make this check for contact with all platforms
        return self.y > FLOOR_HEIGHT

    # ========================= state functions ================================

    def state_stand(self, keys):
        if keys[Keys.JUMP]:  # enter jumpsquat
            self.enter_jumpsquat()
        if keys[Keys.DOWN]:  # enter squat
            self.state = states.SQUAT
        if keys[Keys.LEFT] or keys[Keys.RIGHT]:
            self.state = states.RUN

    def enter_jumpsquat(self):
        self.state = states.JUMPSQUAT
        self.jumpsquat_frames_elapsed = 0

    def state_jumpsquat(self, keys):
        self.jumpsquat_frames_elapsed += 1
        # if end of jumpsquat reached, begin jump
        if self.jumpsquat_frames_elapsed == self.jumpsquat_frames:
            self.jumpsquat_frames_elapsed = None
            self.enter_jump()
        # todo: add any other actions that are allowed in jumpsquat state... wavedash ahem.

    def enter_jump(self):
        self.v = self.jump_power
        self.state = states.FALL
        self.fastfall = False

    def state_fall(self, keys):
        # update vertical position
        # if moving downwards faster than fall speed
        if self.v < 0 and abs(self.v) > self.fall_speed:
            pass  # don't apply gravity
        else:  # if moving upwards, or if falling slower than the fall speed
            self.v -= self.fall_acceleration

        # update horizontal position
        if keys[Keys.LEFT]:
            self.u -= self.air_acceleration
        if keys[Keys.RIGHT]:
            self.u += self.air_acceleration
        if abs(self.u) > self.air_speed:
            self.u = sign(self.u) * self.air_speed

        # fastfall if moving downwards
        if keys[Keys.DOWN] and self.v < 0:
            self.fastfall = True
            self.v = -self.fall_speed

        if not self.airborne:
            self.state = states.STAND

    def state_squat(self, keys):
        if keys[Keys.JUMP]:
            self.enter_jumpsquat()
        # if squat key released, exit squat state
        if not keys[Keys.DOWN]:
            self.state = states.STAND

    def state_run(self, keys):
        if not keys[Keys.LEFT] and not keys[Keys.RIGHT]:
            self.state = states.STAND
        if keys[Keys.LEFT]:
            self.u -= self.ground_acceleration
        if keys[Keys.RIGHT]:
            self.u += self.ground_acceleration
        if abs(self.u) > self.ground_speed:  # enforce run speed
            self.u = sign(self.u) * self.ground_speed
        if keys[Keys.JUMP]:
            self.enter_jumpsquat()
        if keys[Keys.DOWN]:
            self.state = states.SQUAT
