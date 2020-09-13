from collections import deque

import pygame

from base.singleton import Singleton


class Empty(tuple):
    """Mock tuple of 0/1s that always returns a 0 no matter the index. This is used to
    spoof an empty pygame.key.get_pressed() tuple."""

    def __getitem__(self, *args, **kwargs):
        return 0


class InputQueue(deque, Singleton):
    """
    Provides additional functionality beyond pygame.key.get_pressed().
    - Maintains a buffer of the last few inputs
    - Calculates which keys have been pressed and released this tick
    """

    # fixme: should this still be a singleton if I am using multiple gamecube controllers for
    #  example?

    def __init__(self, queue_length=5):
        super().__init__(maxlen=queue_length)

    @classmethod
    def get_new_values(self):
        """ Subclasses should implement this. It should be something like
        pygame.key.get_pressed() """
        raise NotImplementedError

    @classmethod
    def read_new_keypresses(cls):
        cls.append(cls.get_new_values())

    @classmethod
    def append(cls, value):
        instance = cls.get_instance()
        return super().append(instance, value)

    @classmethod
    def get_down(cls):
        """ Return the keys which are currently held down """
        instance = cls.get_instance()
        return instance[-1] if len(instance) > 0 else Empty()

    @classmethod
    def get_pressed(cls):
        """ Return the keys that have just been pressed---i.e. those that are down this tick but
        not the previous tick """
        instance = cls.get_instance()
        try:
            current = instance[-1]
            previous = instance[-2]
            return tuple(int(c and not p) for c, p in zip(current, previous))
        except IndexError:
            return Empty()

    @classmethod
    def get_released(cls):
        """ Return the keys that have just been released---i.e. those that are not down this
        tick, but were down the previous tick """
        instance = cls.get_instance()
        try:
            current = instance[-1]
            previous = instance[-2]
            return tuple(int(p and not c) for c, p in zip(current, previous))
        except IndexError:
            return Empty()

    @classmethod
    def is_pressed(cls, key):
        """ Check if a key has been pressed this tick """
        keys = cls.get_pressed()
        return keys[key]

    @classmethod
    def is_down(cls, key):
        """ Check if a key is currently held down """
        keys = cls.get_down()
        return keys[key]

    @classmethod
    def is_released(cls, key):
        """ Check if a key has been released this tick """
        keys = cls.get_released()
        return keys[key]
