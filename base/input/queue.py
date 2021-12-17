from collections import deque

from base.utils import count_edges


class Empty(tuple):
    """Mock tuple of 0/1s that always returns a 0 no matter the index. This is used to
    spoof an empty pygame.key.get_pressed() tuple."""

    def __getitem__(self, *args, **kwargs):
        return 0


class InputQueue(deque):
    """
    Provides additional functionality beyond pygame.key.get_pressed().
    - Maintains a buffer of the last few inputs
    - Calculates which keys have been pressed and released this tick
    """

    def __init__(self, queue_length=5):
        super().__init__(maxlen=queue_length)

    def get_new_values(self):
        """Subclasses should implement this. It should be something like
        pygame.key.get_pressed()"""
        raise NotImplementedError

    def read_new_inputs(self):
        self.append(self.get_new_values())

    def get_down(self):
        """ Return the keys which are currently held down """
        return self[-1] if len(self) > 0 else Empty()

    def get_pressed(self):
        """Return the keys that have just been pressed---i.e. those that are down this tick but
        not the previous tick"""
        try:
            current = self[-1]
            previous = self[-2]
            return tuple(int(c and not p) for c, p in zip(current, previous))
        except IndexError:
            return Empty()

    def get_released(self):
        """Return the keys that have just been released---i.e. those that are not down this
        tick, but were down the previous tick"""
        try:
            current = self[-1]
            previous = self[-2]
            return tuple(int(p and not c) for c, p in zip(current, previous))
        except IndexError:
            return Empty()

    def is_pressed(self, key):
        """ Check if a key has been pressed this tick """
        keys = self.get_pressed()
        return keys[key]

    def is_down(self, key):
        """ Check if a key is currently held down """
        keys = self.get_down()
        return keys[key]

    def is_released(self, key):
        """ Check if a key has been released this tick """
        keys = self.get_released()
        return keys[key]

    def buffered_inputs(self, key, buffer_length):
        """ Count the rising and falling edges. Can be used to detect past inputs. """
        buffer = list(self)[-buffer_length:]
        values = [layer[key] for layer in buffer]
        return count_edges(values)

    def buffered_presses(self, key, buffer_length):
        rising, falling = self.buffered_inputs(key, buffer_length)
        return rising

    def buffered_releases(self, key, buffer_length):
        rising, falling = self.buffered_inputs(key, buffer_length)
        return falling
