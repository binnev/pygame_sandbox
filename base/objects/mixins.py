from collections import deque
from copy import deepcopy

import pygame

from base.keyhandler import KeyHandler


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
    x: int
    y: int

    class keymap:
        LEFT = pygame.K_LEFT
        RIGHT = pygame.K_RIGHT
        UP = pygame.K_UP
        DOWN = pygame.K_DOWN

    SPEED = 2

    def update_position(self):
        if KeyHandler.is_down(self.keymap.RIGHT):
            self.x += self.SPEED
        if KeyHandler.is_down(self.keymap.LEFT):
            self.x -= self.SPEED
        if KeyHandler.is_down(self.keymap.DOWN):
            self.y += self.SPEED
        if KeyHandler.is_down(self.keymap.UP):
            self.y -= self.SPEED


class CollisionMixin:
    """This mixin requires the subclass to have the following attributes to function"""

    # todo: make this more general. It's too specific to Character that inherits from it.

    rect: pygame.Rect
    centroid: property
    history: deque
    keys: tuple
    is_touching: "method"

    def get_overlap_with_object(self, obj):
        """Get the x and y overlap between self and obj.rect"""
        x_overlap = min(self.rect.right, obj.rect.right) - max(self.rect.left, obj.rect.left)
        y_overlap = min(self.rect.bottom, obj.rect.bottom) - max(self.rect.top, obj.rect.top)
        return x_overlap, y_overlap

    def can_stand_on_droppable_platform(self, platform):
        was_above_platform = self.history[-1]["rect"].bottom <= platform.rect.top
        not_holding_down = not self.keys[Keys.DOWN]
        return self.is_touching(platform) and was_above_platform and not_holding_down

    def can_stand_on_solid_platform(self, platform):
        x_overlap, y_overlap = self.get_overlap_with_object(platform)
        return (
            self.is_touching(platform) and x_overlap > 0 and self.centroid.y < platform.centroid.y
        )

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
        platforms = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
        for platform in platforms:
            if platform.can_fall_through:
                print("colliding with droppable platform")
                self.collide_droppable_platform(platform)
            else:
                print("colliding with platform")
                self.collide_solid_platform(platform)
