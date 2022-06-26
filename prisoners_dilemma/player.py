import random

from prisoners_dilemma.constants import DEFECT, COOPERATE


class Player:
    score: int = 0

    def play_turn(self, self_history, other_history):
        raise NotImplementedError()

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.name}(score={self.score})"

    def __format__(self, format_spec):
        return str.__format__(self.name, format_spec)


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


class TitForTwoTat(Player):
    tolerance = 2

    def play_turn(self, self_history, other_history):
        if other_history and other_history[-1] == DEFECT:
            self.tolerance -= 1

        if self.tolerance == 0:
            self.tolerance = 2
            return DEFECT
        else:
            return COOPERATE


class MostlyNice(Player):
    def play_turn(self, self_history, other_history):
        return random.choice([DEFECT] + [COOPERATE] * 9)


class MostlyNasty(Player):
    def play_turn(self, self_history, other_history):
        return random.choice([COOPERATE] + [DEFECT] * 9)


class NeverForgive(Player):
    def play_turn(self, self_history, other_history):
        if DEFECT in other_history:
            return DEFECT
        else:
            return COOPERATE
