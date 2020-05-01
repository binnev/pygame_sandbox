from collections import deque


class Empty(tuple):
    """Mock tuple of 0/1s that always returns a 0 no matter the index. This is used to
    spoof an empty pygame.key.get_pressed() tuple."""

    def __getitem__(self, *args, **kwargs):
        return 0


class KeyHandler(deque):
    """
    Provides additional functionality beyond pygame.key.get_pressed().
    - Maintains a buffer of the last few keypresses
    - Calculates which keys have been pressed and released this tick
    """

    def __init__(self, queue_length=5):
        super().__init__()
        self.queue_length = queue_length

    # ========== adding / removing items ==========

    def enqueue(self, new_keys):
        self.append(new_keys)

    def dequeue(self):
        self.popleft()

    def discard_old(self):
        if len(self) > self.queue_length:
            self.dequeue()

    def update(self, new_keys):
        self.enqueue(new_keys)
        self.discard_old()

    # ========== getting key information ==========

    def get_down(self):
        """Return the current state of keys---which are currently down"""
        return self[-1] if len(self) > 0 else Empty()

    def get_pressed(self):
        """Return the keys that have just been pressed---i.e. those that are down this
        tick but not the previous tick"""
        try:
            current = self[-1]
            previous = self[-2]
            return tuple(int(c and not p) for c, p in zip(current, previous))
        except IndexError:
            return Empty()

    def get_released(self):
        """Return the keys that have just been released---i.e. those that are not down
        this tick, but were down the previous tick"""
        try:
            current = self[-1]
            previous = self[-2]
            return tuple(int(p and not c) for c, p in zip(current, previous))
        except IndexError:
            return Empty()
