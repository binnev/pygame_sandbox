import pytest

from chess.constants import WHITE, BLACK
from chess.engine.classes.position import Position
from chess.engine.utils import is_in_check


@pytest.mark.parametrize(
    "description, params",
    [
        (
            "starting position",
            dict(
                position="/".join(
                    [
                        "rnbqkbnr",
                        "pppppppp",
                        "........",
                        "........",
                        "........",
                        "........",
                        "PPPPPPPP",
                        "RNBQKBNR",
                    ]
                ),
                team=WHITE,
                expected_result=False,
            ),
        ),
        (
            "with pawn",
            dict(
                position="/".join(
                    [
                        "....k...",
                        "...P....",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                    ]
                ),
                team=BLACK,
                expected_result=True,
            ),
        ),
        (
            "with bishop",
            dict(
                position="/".join(
                    [
                        "........",
                        "........",
                        "........",
                        "........",
                        ".....b..",
                        "........",
                        "...K....",
                        "........",
                    ]
                ),
                team=WHITE,
                expected_result=True,
            ),
        ),
        (
            "with bishop and rook",
            dict(
                position="/".join(
                    [
                        "........",
                        "...r....",
                        "........",
                        "........",
                        ".....b..",
                        "........",
                        "...K....",
                        "........",
                    ]
                ),
                team=WHITE,
                expected_result=True,
            ),
        ),
        (
            "with rook",
            dict(
                position="/".join(
                    [
                        "........",
                        "...r....",
                        "........",
                        "........",
                        "........",
                        "........",
                        "...K....",
                        "........",
                    ]
                ),
                team=WHITE,
                expected_result=True,
            ),
        ),
        (
            "with queen",
            dict(
                position="/".join(
                    [
                        ".......k",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "Q.......",
                    ]
                ),
                team=BLACK,
                expected_result=True,
            ),
        ),
        (
            "shouldn't be check",
            dict(
                position="/".join(
                    [
                        "k.......",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "K.......",
                    ]
                ),
                team=WHITE,
                expected_result=False,
            ),
        ),
        (
            "shouldn't be check",
            dict(
                position="/".join(
                    [
                        "k.......",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        ".K......",
                    ]
                ),
                team=WHITE,
                expected_result=False,
            ),
        ),
        (
            "shouldn't be check",
            dict(
                position="/".join(
                    [
                        "k.......",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "K.......",
                        "........",
                    ]
                ),
                team=WHITE,
                expected_result=False,
            ),
        ),
        (
            "shouldn't be check",
            dict(
                position="/".join(
                    [
                        "k.......",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        ".K......",
                        "........",
                    ]
                ),
                team=WHITE,
                expected_result=False,
            ),
        ),
    ],
)
def test_is_in_check(description, params):
    position = Position.from_fen(params["position"])
    assert is_in_check(params["team"], position) == params["expected_result"]
