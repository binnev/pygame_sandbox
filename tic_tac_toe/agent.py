import random
from math import inf

from .constants import O, X
from .state import State


class Agent:
    team: str  # O | X

    def __init__(self, team: str):
        self.team = team

    def choose_move(self, state: State) -> int:
        raise NotImplementedError


class RandomAgent(Agent):
    def choose_move(self, state: State) -> int:
        return random.choice(state.available_moves)


class CliAgent(Agent):
    def choose_move(self, state: State) -> int:
        while True:
            print("Current state:")
            state.print()
            print(f"Available moves are: {state.available_moves}")
            move = int(input(f"Choose a move: "))
            if move in state.available_moves:
                return move
            else:
                print(f"{move} is not a legal move")


def minimax(state: State, depth: int, team: str):

    if state.is_game_over or depth == 0:
        mapping = {None: 0, O: 1, X: -1}
        return mapping[state.winner]

    if team == O:
        max_score = -inf
        for move in state.available_moves:
            new_state = state.do_move(move)
            score = minimax(new_state, depth - 1, X)
            max_score = max(score, max_score)
        return max_score

    else:
        min_score = inf
        for move in state.available_moves:
            new_state = state.do_move(move)
            score = minimax(new_state, depth - 1, O)
            min_score = min(score, min_score)
        return min_score


class MinimaxAgent(Agent):
    def choose_move(self, state: State) -> int:
        current_score = minimax(state=state, depth=10, team=self.team)
        WINNING = "I will end you, puny human"
        LOSING = "How is this possible! I never lose!"
        DRAW = "You can never defeat me"
        evaluations = {
            1: WINNING if self.team == O else LOSING,
            -1: LOSING if self.team == O else WINNING,
            0: DRAW,
        }
        print(evaluations[current_score])
        move_scores = {}
        for move in state.available_moves:
            new_state = state.do_move(move)
            move_scores[move] = minimax(state=new_state, depth=10, team=X if self.team == O else O)

        func = max if self.team == O else min
        return func(move_scores, key=lambda k: move_scores[k])