import random

from .state import State


class Agent:
    def choose_move(self, state: "State") -> int:
        raise NotImplementedError


class RandomAgent(Agent):
    def choose_move(self, state: "State") -> int:
        return random.choice(state.available_moves)


class CliAgent(Agent):
    def choose_move(self, state: "State") -> int:
        while True:
            print("Current state:")
            state.print()
            print(f"Available moves are: {state.available_moves}")
            move = int(input(f"Choose a move: "))
            if move in state.available_moves:
                return move
            else:
                print(f"{move} is not a legal move")
