from collections import deque

from robingame.objects import Entity
from robingame.utils import SparseMatrix

from automata.automatons import Automaton
from automata.timer import Timer


class Backend(Entity):
    """
    Adapts Automaton for use in the pygame game loop

    Inherits Entity
    Contains Automaton
    Implements update/iterate disconnect
    Implements history
    """

    automaton: Automaton

    ticks_per_update: int = 1
    iterations_per_update: int = 1
    paused: bool = False
    history: deque[SparseMatrix]
    _update_time = 0

    def __init__(self, automaton: Automaton):
        super().__init__()
        self.automaton = automaton
        self.history = deque(maxlen=50)

    def update(self):
        with Timer() as timer:
            super().update()
            if not self.paused and self.tick % self.ticks_per_update == 0:
                for _ in range(self.iterations_per_update):
                    # delegate iteration to the automaton
                    self.iterate()
        self._update_time = timer.time

    def iterate(self):
        self.history.append(self.automaton.contents)
        self.automaton.iterate()

    def back_one(self):
        if self.history:
            self.automaton.contents = self.history.pop()
