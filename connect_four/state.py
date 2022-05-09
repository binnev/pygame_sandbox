EMPTY = "."
RED = "O"
YELLOW = "X"


class State(str):
    """
    Immutable class representing a state of connect-4.
    Connect-4 has 7 columns of height 6. We represent each column as a 6-length string of either
    empty / red / yellow values. The columns are joined by slashes.

    For example, the empty "board" would be represented as:
    "....../....../....../....../....../....../......"
    """

    height = 6
    width = 7

    def __init__(self, string):
        self.player_to_move = player_to_move(self)
        self.available_moves = available_moves(self)
        self.is_game_over, self.winner = is_game_over(self)

    @classmethod
    def initial(cls):
        return cls("/".join(["." * cls.height] * cls.width))

    def to_string(self):
        return "\n".join(
            "".join(column[row] for column in self.split("/"))
            for row in reversed(range(self.height))
        )

    def print(self):
        print(self.to_string())

    def do_move(self, move: int):
        columns = [[char for char in col if char != EMPTY] for col in self.split("/")]
        columns[move].append(self.player_to_move)
        new_string = "/".join("".join(col).ljust(State.height, ".") for col in columns)
        return State(new_string)


def player_to_move(state: State) -> str | None:
    """Yellow goes first"""
    reds = state.count(RED)
    yellows = state.count(YELLOW)
    if reds < yellows:
        return RED
    if yellows == reds:
        return YELLOW


def available_moves(state: State) -> tuple[int]:
    """Players can put a piece in any of the columns that are not full"""
    columns = state.split("/")
    return tuple(index for index, column in enumerate(columns) if column[-1] == EMPTY)


def get_diagonal_win_vectors():
    diagonals = []
    for ii in range(3, State.height + State.width - 4):
        diagonals.append(
            tuple(
                h + w * (State.height + 1)
                for w in range(State.width)
                for h in range(State.height)
                if h + w == ii
            )
        )
    for ii in range(3, State.height + State.width - 4):
        diagonals.append(
            tuple(
                h + w * (State.height + 1)
                for w in range(State.width)
                for h in reversed(range(State.height))
                if (State.height - h - 1) + w == ii
            )
        )
    return tuple(diagonals)


def get_row_win_vectors():
    vectors = []
    vectors.extend(
        (tuple(h + w * (State.height + 1) for h in range(State.height)) for w in range(State.width))
    )
    vectors.extend(
        (tuple(h + w * (State.height + 1) for w in range(State.width)) for h in range(State.height))
    )
    return tuple(vectors)


WIN_VECTORS = (*get_row_win_vectors(), *get_diagonal_win_vectors())


def is_game_over(state: State) -> (bool, str | None):
    for vector in WIN_VECTORS:
        values = "".join(state[i] for i in vector)
        if RED * 4 in values:
            return True, RED
        if YELLOW * 4 in values:
            return True, YELLOW
    if EMPTY not in state:
        return True, None
    return False, None
