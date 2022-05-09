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
    assert set(diagonals[0]) == {3, 9, 15, 21}
    assert set(diagonals[-1]) == {26, 32, 38, 44}
