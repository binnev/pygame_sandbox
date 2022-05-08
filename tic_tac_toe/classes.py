import random
from dataclasses import dataclass

O = "o"
X = "x"
EMPTY = "."


class State(str):
    """
    len 9 string to store a tic-tac-toe game state:
    o| |
    -+-+-
     |x|   = "o...x...o"
    -+-+-
     | |o

    indices of the squares are:
    0|1|2
    -+-+-
    3|4|5
    -+-+-
    6|7|8
    """

    def __init__(self, string):
        """GameState is immutable, so we can calculate properties once at init"""
        self.player_to_move = player_to_move(self)
        self.available_moves = available_moves(self)
        self.is_game_over, self.winner = is_game_over(self)

    def to_string(self) -> str:
        with_spaces = self.replace(EMPTY, " ")
        rows = [with_spaces[0:3], with_spaces[3:6], with_spaces[6:9]]
        return "\n-+-+-\n".join("|".join(row) for row in rows)

    def print(self):
        print(self.to_string())

    def do_move(self, move: int) -> "State":
        chars = list(self)
        chars[move] = self.player_to_move
        return State("".join(chars))

    @classmethod
    def initial(cls) -> "State":
        return cls(".........")


def player_to_move(state: State) -> str | None:
    os = state.count(O)
    xs = state.count(X)
    if xs < os:
        return X
    if xs == os:
        return O


def available_moves(state: State) -> tuple[int]:
    return tuple(index for index, char in enumerate(state) if char == EMPTY)


WIN_VECTORS = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


def is_game_over(state: State) -> (bool, str | None):
    """is_over, winner = is_game_over(state)"""
    if EMPTY not in state:
        return True, None
    for vector in WIN_VECTORS:
        values = [state[i] for i in vector]
        if values == [X, X, X]:
            return True, X
        if values == [O, O, O]:
            return True, O
    return False, None


class Match:
    history: list[tuple[int | None, State]]

    def __init__(self, initial_state: State = None):
        state = initial_state or State.initial()
        self.history = []
        self.history.append((None, state))

    def do_move(self, move: int):
        next_state = self.current_state.do_move(move)
        self.history.append((move, next_state))

    @property
    def current_state(self):
        return self.history[-1][1]

    @property
    def is_active(self) -> bool:
        return not self.current_state.is_game_over

    @property
    def player_to_move(self):
        return self.current_state.player_to_move


class Agent:
    def choose_move(self, state: State) -> int:
        raise NotImplementedError


class RandomAgent(Agent):
    def choose_move(self, state: State) -> int:
        return random.choice(state.available_moves)


class HumanAgent(Agent):
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


@dataclass
class Controller:
    """Currently this is implicitly running a match for the CLI. Might need to create specific
    subclasses for GUI"""

    agent_o: Agent
    agent_x: Agent
    match: Match

    def get_agent(self, player: str) -> Agent:
        return {X: self.agent_x, O: self.agent_o}[player]

    def display_turn(self):
        raise NotImplementedError

    def run_turn(self):
        player = self.match.player_to_move
        agent = self.get_agent(player)
        move = agent.choose_move(self.match.current_state)
        self.match.do_move(move)

    def run_match(self):
        while self.match.is_active:
            self.run_turn()
            self.display_turn()
        self.handle_match_end()

    def handle_match_end(self):
        raise NotImplementedError


class CliController(Controller):
    def display_turn(self):
        player = self.match.player_to_move
        move = self.match.history[-1][0]
        print(f"Player {player} has chosen move {move}")
        self.match.current_state.print()

    def handle_match_end(self):
        winner = self.match.current_state.winner or "no-one"
        print(f"congratulations to {winner}!")
