import random

from prisoners_dilemma.constants import DEFECT, COOPERATE


class Player:
    name: str

    def play_turn(self, self_history, other_history):
        raise NotImplementedError()

    def __str__(self):
        return self.__class__.__name__


class RandomPlayer(Player):
    def play_turn(self, self_history, other_history):
        return random.choice([DEFECT, COOPERATE])


class AlwaysDefect(Player):
    def play_turn(self, self_history, other_history):
        return DEFECT


class AlwaysCooperate(Player):
    def play_turn(self, self_history, other_history):
        return COOPERATE

class TitForTat(Player):
    def play_turn(self, self_history, other_history):
        if other_history and other_history[-1] == DEFECT:
            return DEFECT
        else:
            return COOPERATE