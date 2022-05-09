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

    @classmethod
    def initial(cls):
        return cls("/".join(["." * cls.height] * cls.width))

    def to_string(self):
        return "\n".join(
            "".join(column[row] for column in self.split("/"))
            for row in reversed(range(self.height))
        )


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


def get_diagonals():
    diagonals = []
    for ii in range(3, State.height + State.width - 4):
        diagonal = []
        for w in range(State.width):
            for h in range(State.height):
                if h + w == ii:
                    flat_index = h + w * (State.height + 1)
                    diagonal.append(flat_index)
        diagonals.append(tuple(diagonal))
    return tuple(diagonals)
