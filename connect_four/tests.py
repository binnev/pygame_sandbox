import pytest

from connect_four.state import State, available_moves, get_diagonals


def test_state_initial():
    assert State.initial() == "....../....../....../....../....../....../......"


def test_state_to_string():
    state = State("OOO.../XX..../O...../....../....../....../XXXOOO")
    assert state.to_string() == "\n".join(
        (
            "......O",
            "......O",
            "......O",
            "O.....X",
            "OX....X",
            "OXO...X",
        )
    )


@pytest.mark.parametrize(
    "state_string, expected_available_moves",
    [
        ("....../....../....../....../....../....../......", (0, 1, 2, 3, 4, 5, 6)),
        ("OOOOOO/....../....../....../....../....../......", (1, 2, 3, 4, 5, 6)),
        ("OOOOOO/OOOOOO/OOOOOO/OOOOOO/OOOOOO/OOOOOO/OOOOOO", tuple()),
    ],
)
def test_available_moves(state_string, expected_available_moves):
    state = State(state_string)
    assert available_moves(state) == expected_available_moves


def test_get_diagonals():
    diagonals = get_diagonals()
    assert diagonals == (
        (3, 9, 15, 21),
        (4, 10, 16, 22, 28),
        (5, 11, 17, 23, 29, 35),
        (12, 18, 24, 30, 36, 42),
        (19, 25, 31, 37, 43),
        (26, 32, 38, 44),
        (2, 10, 18, 26),
        (1, 9, 17, 25, 33),
        (0, 8, 16, 24, 32, 40),
        (7, 15, 23, 31, 39, 47),
        (14, 22, 30, 38, 46),
        (21, 29, 37, 45),
    )
