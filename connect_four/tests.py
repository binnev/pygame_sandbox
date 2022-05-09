import pytest

from connect_four.state import (
    State,
    available_moves,
    get_diagonal_win_vectors,
    get_row_win_vectors,
    is_game_over,
    YELLOW,
    RED,
)


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


def test_get_diagonal_win_vectors():
    diagonals = get_diagonal_win_vectors()
    assert set(diagonals) == {
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
    }


def test_get_row_win_vectors():
    vectors = get_row_win_vectors()
    assert vectors[0] == (0, 1, 2, 3, 4, 5)
    assert vectors[6] == (42, 43, 44, 45, 46, 47)
    assert vectors[7] == (0, 7, 14, 21, 28, 35, 42)
    assert vectors[12] == (5, 12, 19, 26, 33, 40, 47)


@pytest.mark.parametrize(
    "state, expected_result",
    [
        (
            "/".join(
                [
                    "......",
                    "......",
                    "......",
                    "......",
                    "......",
                    "......",
                    "......",
                ]
            ),
            (False, None),
        ),
        (
            "/".join(
                [
                    "......",
                    ".....X",
                    "....X.",
                    "...X..",
                    "..X...",
                    ".X....",
                    "X.....",
                ]
            ),
            (True, YELLOW),
        ),
        (
            "/".join(
                [
                    "......",
                    "......",
                    "......",
                    "O.....",
                    ".O....",
                    "..O...",
                    "...O..",
                ]
            ),
            (True, RED),
        ),
        (
            "/".join(
                [
                    ".O...X",
                    "....X.",
                    "...O..",
                    "..X.O.",
                    ".X...O",
                    "X.....",
                    "......",
                ]
            ),
            (False, None),
        ),
        (
            "/".join(
                [
                    "......",
                    "O.....",
                    "......",
                    "O.....",
                    "O.....",
                    "O.....",
                    "XXX.XX",
                ]
            ),
            (False, None),
        ),
        (
            "/".join(
                [
                    "XXXOOO",
                    "XXXOOO",
                    "XXXOOO",
                    "......",
                    "XXXOOO",
                    "XXXOOO",
                    "XXXOOO",
                ]
            ),
            (False, None),
        ),
        (
            "/".join(
                [
                    "......",
                    "......",
                    "......",
                    ".....X",
                    "....XO",
                    "...XOO",
                    "..XOOO",
                ]
            ),
            (True, YELLOW),
        ),
        (
            "/".join(
                [
                    "......",
                    "......",
                    "......",
                    "......",
                    "......",
                    "......",
                    "OOOOOO",
                ]
            ),
            (True, RED),
        ),
        (
            "/".join(
                [
                    "X.....",
                    "X.....",
                    "X.....",
                    "X.....",
                    "X.....",
                    "X.....",
                    "X.....",
                ]
            ),
            (True, YELLOW),
        ),
        (
            "/".join(
                [
                    "......",
                    "......",
                    "......",
                    "......",
                    ".....O",
                    ".....O",
                    "XXX..O",
                ]
            ),
            (False, None),
        ),
    ],
)
def test_is_game_over(state, expected_result):
    state = State(state)
    assert is_game_over(state) == expected_result


def test_state_do_move():
    state = State.initial()
    state = state.do_move(0)
    assert state == "X...../....../....../....../....../....../......"
    state = state.do_move(0)
    assert state == "XO..../....../....../....../....../....../......"
    state = state.do_move(0)
    assert state == "XOX.../....../....../....../....../....../......"
    state = state.do_move(6)
    assert state == "XOX.../....../....../....../....../....../O....."
