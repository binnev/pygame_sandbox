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
from connect_four.team import TEAM_YELLOW, TEAM_RED


def test_state_initial():
    assert State.initial() == "....../....../....../....../....../....../......"


def test_state_to_string():
    state = State("OOO.../XX..../O...../....../....../....../XXXOOO")
    assert state.to_string() == "\n".join(
        (
            ". . . . . . O",
            ". . . . . . O",
            ". . . . . . O",
            "O . . . . . X",
            "O X . . . . X",
            "O X O . . . X",
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
            (False, 0),
        ),
        (
            "/".join(
                [
                    "......",
                    ".....x",
                    "....x.",
                    "...x..",
                    "..x...",
                    ".x....",
                    "x.....",
                ]
            ),
            (True, TEAM_YELLOW.win_value),
        ),
        (
            "/".join(
                [
                    "......",
                    "......",
                    "......",
                    "o.....",
                    ".o....",
                    "..o...",
                    "...o..",
                ]
            ),
            (True, TEAM_RED.win_value),
        ),
        (
            "/".join(
                [
                    ".o...x",
                    "....x.",
                    "...o..",
                    "..x.o.",
                    ".x...o",
                    "x.....",
                    "......",
                ]
            ),
            (False, 0),
        ),
        (
            "/".join(
                [
                    "......",
                    "o.....",
                    "......",
                    "o.....",
                    "o.....",
                    "o.....",
                    "xxx.xx",
                ]
            ),
            (False, 0),
        ),
        (
            "/".join(
                [
                    "xxxooo",
                    "xxxooo",
                    "xxxooo",
                    "......",
                    "xxxooo",
                    "xxxooo",
                    "xxxooo",
                ]
            ),
            (False, 0),
        ),
        (
            "/".join(
                [
                    "......",
                    "......",
                    "......",
                    ".....x",
                    "....xo",
                    "...xoo",
                    "..xooo",
                ]
            ),
            (True, TEAM_YELLOW.win_value),
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
                    "oooooo",
                ]
            ),
            (True, TEAM_RED.win_value),
        ),
        (
            "/".join(
                [
                    "x.....",
                    "x.....",
                    "x.....",
                    "x.....",
                    "x.....",
                    "x.....",
                    "x.....",
                ]
            ),
            (True, TEAM_YELLOW.win_value),
        ),
        (
            "/".join(
                [
                    "......",
                    "......",
                    "......",
                    "......",
                    ".....o",
                    ".....o",
                    "xxx..o",
                ]
            ),
            (False, 0),
        ),
    ],
)
def test_is_game_over(state, expected_result):
    state = State(state)
    assert is_game_over(state) == expected_result


def test_state_do_move():
    state = State.initial()
    state = state.do_move(0)
    assert state == "x...../....../....../....../....../....../......"
    state = state.do_move(0)
    assert state == "xo..../....../....../....../....../....../......"
    state = state.do_move(0)
    assert state == "xox.../....../....../....../....../....../......"
    state = state.do_move(6)
    assert state == "xox.../....../....../....../....../....../o....."


"""
todo: the minimax agent thinks this position is lost, and picks a random losing move. 
Why doesn't it just block the vertical 4?

Available moves are: (0, 1, 2, 3, 4, 5, 6)
Choose a move: 4
Player x has chosen move 4
. . . . . . .
. . . . . . .
. . . . . . .
. . . x x . .
. . . o x o .
. o o x x x o



also this random blunder: 
AI: 'You can never defeat me'
Player o has chosen move 5
. . . . . . .
. . . . . . .
. . . o . . .
. . . x x . .
. . x x o o .
. . o x x o o
--------------------------------------------------------------------------------
Available moves are: (0, 1, 2, 3, 4, 5, 6)
Choose a move: 4
Player x has chosen move 4
. . . . . . .
. . . . . . .
. . . o x . .
. . . x x . .
. . x x o o .
. . o x x o o
--------------------------------------------------------------------------------
AI: 'How is this possible! I never lose!'
Player o has chosen move 6
. . . . . . .
. . . . . . .
. . . o x . .
. . . x x . .
. . x x o o o
. . o x x o o

maybe something with the caching? that it doesn't include the depth in the cache?
"""
