from collections import deque

from base.singleton import Singleton


class Empty(tuple):
    """Mock tuple of 0/1s that always returns a 0 no matter the index. This is used to
    spoof an empty pygame.key.get_pressed() tuple."""

    def __getitem__(self, *args, **kwargs):
        return 0


class KeyHandler(deque, Singleton):
    """
    Provides additional functionality beyond pygame.key.get_pressed().
    - Maintains a buffer of the last few keypresses
    - Calculates which keys have been pressed and released this tick
    """

    def __init__(self, queue_length=5):
        super().__init__(maxlen=queue_length)

    @classmethod
    def append(cls, value):
        instance = cls.get_instance()
        return super().append(instance, value)

    @classmethod
    def get_down(cls):
        """Return the current state of keys---which are currently down"""
        instance = cls.get_instance()
        return instance[-1] if len(instance) > 0 else Empty()

    @classmethod
    def get_pressed(cls):
        """Return the keys that have just been pressed---i.e. those that are down this
        tick but not the previous tick"""
        instance = cls.get_instance()
        try:
            current = instance[-1]
            previous = instance[-2]
            return tuple(int(c and not p) for c, p in zip(current, previous))
        except IndexError:
            return Empty()

    @classmethod
    def get_released(cls):
        """Return the keys that have just been released---i.e. those that are not down
        this tick, but were down the previous tick"""
        instance = cls.get_instance()
        try:
            current = instance[-1]
            previous = instance[-2]
            return tuple(int(p and not c) for c, p in zip(current, previous))
        except IndexError:
            return Empty()

    @classmethod
    def is_pressed(cls, key):
        keys = cls.get_pressed()
        return keys[key]

    @classmethod
    def is_down(cls, key):
        keys = cls.get_down()
        return keys[key]

    @classmethod
    def is_released(cls, key):
        keys = cls.get_released()
        return keys[key]

