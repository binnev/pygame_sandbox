from collections import deque

from robingame.objects import Entity
from robingame.utils import SparseMatrix

from automata.automatons import Automaton


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

    def __init__(self, automaton: Automaton):
        super().__init__()
        self.automaton = automaton
        self.history = deque(maxlen=50)

    def update(self):
        super().update()
        if not self.paused and self.tick % self.ticks_per_update == 0:
            for _ in range(self.iterations_per_update):
                # delegate iteration to the automaton
                self.iterate()

    def iterate(self):
        self.history.append(self.automaton.contents)
        self.automaton.iterate()

    def back_one(self):
        if self.history:
            self.automaton.contents = self.history.pop()
