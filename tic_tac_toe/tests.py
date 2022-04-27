import pytest

from tic_tac_toe.classes import GameState, player_to_move, available_moves, is_game_over, O, X


def test_game_state_to_string():
    state = GameState("o...x...o")
    assert state.to_string() == "\n".join(
        (
            "o| | ",
            "-+-+-",
            " |x| ",
            "-+-+-",
            " | |o",
        )
    )


@pytest.mark.parametrize(
    "initial_state, move, expected_state",
    [
        ("o...x...o", 1, "ox..x...o"),
        ("....x...o", 0, "o...x...o"),
        ("....o....", 0, "x...o...."),
        ("....o....", 8, "....o...x"),
    ],
)
def test_game_state_do_move(initial_state, move, expected_state):
    state = GameState(initial_state)
    state = state.do_move(move)
    assert state == expected_state


def test_game_state_init():
    state = GameState("ooo......")
    assert state.is_game_over is True
    assert state.winner == O
    assert state.player_to_move == X
    assert state.available_moves == (3, 4, 5, 6, 7, 8)


@pytest.mark.parametrize(
    "state, expected_player",
    [
        ("o...x...o", "x"),
        ("....x...o", "o"),
        ("....o....", "x"),
        ("....o....", "x"),
    ],
)
def test_player_to_move(state, expected_player):
    state = GameState(state)
    assert player_to_move(state) == expected_player


@pytest.mark.parametrize(
    "state, expected_moves",
    [
        ("o...x...o", (1, 2, 3, 5, 6, 7)),
        ("oxoxooxoo", ()),
        ("oxoxooxo.", (8,)),
        (".xoxooxoo", (0,)),
    ],
)
def test_available_moves(state, expected_moves):
    state = GameState(state)
    assert available_moves(state) == expected_moves


@pytest.mark.parametrize(
    "state, expected_result",
    [
        (".........", (False, None)),
        ("ooo......", (True, O)),
        ("x...x...x", (True, X)),
        ("x....x..x", (False, None)),
        ("xoxxoxoxo", (True, None)),
    ],
)
def test_is_game_over(state, expected_result):
    state = GameState(state)
    assert is_game_over(state) == expected_result
