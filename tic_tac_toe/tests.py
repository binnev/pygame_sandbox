import pytest
from .match import Match
from .state import State, player_to_move, available_moves, is_game_over
from .controller import CliController
from .agent import RandomAgent, minimax, evaluate_moves

from .constants import X, O


def test_game_state_to_string():
    state = State("o...x...o")
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
    state = State(initial_state)
    state = state.do_move(move)
    assert state == expected_state


def test_game_state_init():
    state = State("ooo......")
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
    state = State(state)
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
    state = State(state)
    assert available_moves(state) == expected_moves


@pytest.mark.parametrize(
    "state, expected_result",
    [
        (".........", (False, None)),
        ("ooo......", (True, O)),
        ("x...x...x", (True, X)),
        ("x....x..x", (False, None)),
        ("xoxxoxoxo", (True, None)),
        ("ooxxooxox", (True, O)),
    ],
)
def test_is_game_over(state, expected_result):
    state = State(state)
    assert is_game_over(state) == expected_result


def test_match_init():
    match = Match()
    assert match.history == [(None, State.initial())]

    custom_state = State("oxo......")
    match = Match(initial_state=custom_state)
    assert match.history == [(None, custom_state)]


def test_match_do_move():
    match = Match()
    match.do_move(8)
    match.do_move(0)
    assert match.history == [
        (None, State.initial()),
        (8, State("........o")),
        (0, State("x.......o")),
    ]


def test_controller_run_match():
    controller = CliController(
        agent_o=RandomAgent(team=O), agent_x=RandomAgent(team=X), match=Match()
    )
    controller.run_match()
    # earliest possible win is after 3 O moves, 2 X moves.
    assert len(controller.match.history) > 5


@pytest.mark.parametrize(
    "state_string, expected_score",
    [
        (
            "".join(
                [
                    "oox",
                    "xoo",
                    "xox",
                ]
            ),
            1,
        ),
        (
            "".join(
                [
                    "oox",
                    "xoo",
                    "oxx",
                ]
            ),
            0,
        ),
        (
            "".join(
                [
                    "o.x",
                    "oox",
                    "..x",
                ]
            ),
            -1,
        ),
        (
            "".join(
                [
                    "...",
                    "xo.",
                    "...",
                ]
            ),
            1,
        ),
        (
            "".join(
                [
                    "o..",
                    "...",
                    "..x",
                ]
            ),
            1,
        ),
        (
            "".join(
                [
                    "...",
                    "ox.",
                    "...",
                ]
            ),
            0,
        ),
        (
            "".join(
                [
                    "x..",
                    "oxo",
                    "...",
                ]
            ),
            -1,
        ),
    ],
)
def test_minimax(state_string, expected_score):
    state = State(state_string)
    assert minimax(state=state, depth=10, is_o=True) == expected_score


@pytest.mark.parametrize(
    "state_string, expected_score",
    [
        (
            "".join(
                [
                    "oox",
                    "xoo",
                    "xox",
                ]
            ),
            1,
        ),
        (
            "".join(
                [
                    "oox",
                    "xoo",
                    "oxx",
                ]
            ),
            0,
        ),
        (
            "".join(
                [
                    "o.x",
                    "oox",
                    "..x",
                ]
            ),
            -1,
        ),
        (
            "".join(
                [
                    "...",
                    "xo.",
                    "...",
                ]
            ),
            {
                0: 1,
                1: 1,
                2: 1,
                5: 0,
                6: 1,
                7: 1,
                8: 1,
            },
        ),
        (
            "".join(
                [
                    "o..",
                    "...",
                    "..x",
                ]
            ),
            {
                1: -1,
                2: 1,
                3: -1,
                4: 0,
                5: 0,
                6: 1,
                7: 0,
            },
        ),
        (
            "".join(
                [
                    "...",
                    "ox.",
                    "...",
                ]
            ),
            {
                0: 0,
                1: 0,
                2: 0,
                5: -1,
                6: 0,
                7: 0,
                8: 0,
            },
        ),
        (
            "".join(
                [
                    "x..",
                    "oxo",
                    "...",
                ]
            ),
            {
                1: -1,
                2: -1,
                6: -1,
                7: -1,
                8: -1,
            },
        ),
    ],
)
def test_evaluate_moves(state_string, expected_score):
    state = State(state_string)
    assert evaluate_moves(state=state, depth=10, is_o=True) == expected_score
