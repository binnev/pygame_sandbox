import random
from functools import lru_cache
from math import inf

from .state import State
from .team import Team


class Agent:
    team: Team

    def __init__(self, team: Team):
        self.team = team

    def choose_move(self, state: State) -> int:
        raise NotImplementedError


class RandomAgent(Agent):
    def choose_move(self, state: State) -> int:
        return random.choice(state.available_moves)


class HumanCliAgent(Agent):
    def choose_move(self, state: State) -> int:
        while True:
            print(f"Available moves are: {state.available_moves}")
            move = int(input(f"Choose a move: "))
            if move in state.available_moves:
                return move
            else:
                print(f"{move} is not a legal move")


@lru_cache(maxsize=1000000)
def minimax(state: State, depth: int, team: bool) -> int:
    """Evaluate all possible moves and return a score describing the position.
    Team True wins if scores are positive; team False wins if scores are negative."""

    # base case
    if state.is_game_over or depth == 0:
        return state.winner

    # recursive case
    best_score = -inf if team else inf
    func = max if team else min
    for move in state.available_moves:
        new_state = state.do_move(move)
        score = minimax(state=new_state, depth=depth - 1, team=not team)
        best_score = func(score, best_score)
    return best_score


def evaluate_moves(state: State, depth: int, team: bool) -> dict[int:int]:
    """Evaluate all possible moves and return a dictionary of move scores.
    If game is over, return empty dict because no moves are available."""
    moves = {}
    if not state.is_game_over:
        for move in state.available_moves:
            new_state = state.do_move(move)
            score = minimax(state=new_state, depth=depth - 1, team=not team)
            moves[move] = score
    return moves


class MinimaxAgent(Agent):
    depth: int

    def __init__(self, team: Team, depth=10):
        self.depth = depth
        super().__init__(team)

    def choose_move(self, state: State) -> int:
        moves = evaluate_moves(state=state, depth=self.depth, team=self.team.boolean)
        func = max if self.team.boolean else min
        best_outcome = func(moves.values())
        best_moves = [k for k, v in moves.items() if v == best_outcome]
        return random.choice(best_moves)


class MinimaxCliAgent(MinimaxAgent):
    def choose_move(self, state: State) -> int:
        moves = evaluate_moves(state=state, depth=self.depth, team=self.team.boolean)
        func = max if self.team.boolean else min
        best_outcome = func(moves.values())
        best_moves = [k for k, v in moves.items() if v == best_outcome]
        WINNING = "I will end you, puny human"
        LOSING = "How is this possible! I never lose!"
        DRAW = "You can never defeat me"
        evaluations = {
            1: WINNING if self.team.boolean else LOSING,
            -1: LOSING if self.team.boolean else WINNING,
            0: DRAW,
        }
        print(f"AI: {evaluations[best_outcome]!r}")
        return random.choice(best_moves)
