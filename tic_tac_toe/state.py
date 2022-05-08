from tic_tac_toe.constants import X, O, EMPTY


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
