from collections import deque
from copy import deepcopy

import pygame


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
    airborne: bool  # make some property to update this value dynamically

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
        self.history.append(
            {attr: deepcopy(getattr(self, attr)) for attr in self.attributes_to_remember}
        )



class SimpleMovementMixin:
    class Keys:
        LEFT = pygame.K_LEFT
        RIGHT = pygame.K_RIGHT
        UP = pygame.K_UP
        DOWN = pygame.K_DOWN

    SPEED = 2

    def update_position(self, keys):
        self.keys = keys
        if keys[self.Keys.RIGHT]:
            self.x += self.SPEED
        if keys[self.Keys.LEFT]:
            self.x -= self.SPEED
        if keys[self.Keys.DOWN]:
            self.y += self.SPEED
        if keys[self.Keys.UP]:
            self.y -= self.SPEED


