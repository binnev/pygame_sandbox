import pygame

from tutorial.conf import SCREEN_WIDTH, SCREEN_HEIGHT, FLOOR_HEIGHT
from tutorial.states import JUMPSQUAT, JUMPING, SQUAT, STANDING, RUNNING
"""
Try shapely: https://shapely.readthedocs.io/en/latest/manual.html
For intersections of hitboxes, hurtboxes, etc
"""


class Thing:
    # class properties (constants)
    width = 40
    height = 60
    ground_acceleration = 5
    ground_speed = 5
    air_acceleration = 7
    air_speed = 7
    fall_acceleration = 2
    fall_speed = 15
    jump_power = 40
    jumpsquat_frames = 2

    # these are really instance variables...
    state = None
    jumpsquat_frames_elapsed = 0

    def __init__(self, x, y, height, width, u=None, v=None):
        self.x = x
        self.y = y
        self.u = u if u else 0
        self.v = v if v else 0
        self._height = height
        self._width = width
        self.keypress_lookup = {
            pygame.K_LEFT: self.keypress_left,
            pygame.K_RIGHT: self.keypress_right,
            pygame.K_DOWN: self.keypress_down,
            pygame.K_SPACE: self.keypress_space,
        }

    @property
    def color(self):
        # if not actionable
        if self.state in [JUMPSQUAT, SQUAT]:
            _color = (255, 0, 0)
        else:
            _color = (255, 255, 255)
        return _color

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        """this is clumsy. Have the jumpsquat state edit the property"""
        if self.state in (JUMPSQUAT, SQUAT):
            return self._height * 0.8
        return self._height

    def draw(self, window):
        pygame.draw.rect(
            window,
            self.color,
            (self.x, self.y, self.width, self.height),
        )

    def debug_print(self):
        print(
            f"state = {self.state},",
            f"airborne = {self.airborne},",
            f"x = {self.x:.2f},",
            f"y = {self.y:.2f},",
            f"u = {self.u:.2f},",
            f"v = {self.v:.2f},",
            f"jumpsquat_frames_elapsed = {self.jumpsquat_frames_elapsed}",
        )

    def update(self, keys, window):
        self.handle_keypresses(keys)
        self.increment_jumpsquat()
        self.increment_squat()
        self.debug_print()
        self.move()
        self.draw(window)

    def move(self):

        # update vertical position
        if self.airborne or self.state == JUMPING:
            # if moving downwards faster than fall speed
            if self.v < 0 and abs(self.v) > self.fall_speed:
                pass  # don't apply gravity
            else:  # if moving upwards, or if falling slower than the fall speed
                self.v -= self.fall_acceleration

        # finally, update position
        self.y += self.v
        self.x += self.u

        if self.airborne:
            self.u *= .7
        else:
            self.u *= .5  # "friction"

        # enforce screen limits
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

    def handle_keypresses(self, keys):
        # todo: move this dict somewhere so it isn't evaluated every tick
        for keypress, func in self.keypress_lookup.items():
            if keys[keypress]:  # if key pressed
                func()  # execute handler function

    def increment_jumpsquat(self):
        # if already in jumpsquat, increment frames elapsed.
        if self.state == JUMPSQUAT:
            self.jumpsquat_frames_elapsed += 1
            # if end of jumpsquat reached, begin jump
            if self.jumpsquat_frames_elapsed == self.jumpsquat_frames:
                self.v = self.jump_power
                print(f"beginning jump. vertical_velocity = {self.u}")
                self.state = JUMPING
                self.jumpsquat_frames_elapsed = 0

    def increment_squat(self):
        if self.state == SQUAT:
            pass
            # if squat key released, exit squat state

    def keypress_space(self):
        if (True
            # not self.airborne
            and self.state not in [JUMPSQUAT]
        ):
            self.state = JUMPSQUAT
            self.jumpsquat_frames_elapsed = 0

    def keypress_left(self):
        # todo: only able to run in actionable states
        if self.airborne and abs(self.u) < self.air_speed:
            self.u -= self.air_acceleration
        if not self.airborne and abs(self.u) < self.ground_speed:
            self.u -= self.ground_acceleration

    def keypress_right(self):
        if self.airborne and abs(self.u) < self.air_speed:
            self.u += self.air_acceleration
        if not self.airborne and abs(self.u) < self.ground_speed:
            self.u += self.ground_acceleration

    def keypress_down(self):
        if self.airborne:
            pass  # implement fast-fall
        else:
            self.state = SQUAT

    @property
    def airborne(self):
        return self.y > FLOOR_HEIGHT
