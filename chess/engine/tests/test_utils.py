import pytest

from chess.constants import WHITE, BLACK, KING, PAWN, BISHOP, KNIGHT, ROOK
from chess.engine.classes.piece import Piece
from chess.engine.classes.position import Position
from chess.engine.classes.square import Square
from chess.engine.utils import is_in_check, get_squares, is_checkmated


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


def test_get_squares_king():
    position = Position()
    assert get_squares(
        current_square=Square(1, 1),
        position=position,
        piece=Piece(WHITE, KING),
    ) == {
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 2),
        (2, 0),
        (2, 1),
        (2, 2),
    }


def test_get_squares_king_obstructed():
    position = Position()
    position.add(Piece(WHITE, PAWN), (1, 1))
    position.add(Piece(BLACK, BISHOP), (0, 1))

    assert get_squares(
        current_square=Square(0, 0),
        position=position,
        piece=Piece(WHITE, KING),
    ) == {
        (0, 1),  # enemy bishop
        (1, 0),  # empty square
    }


def test_get_squares_knight():
    position = Position()
    assert get_squares(
        current_square=Square(5, 5),
        position=position,
        piece=Piece(WHITE, KNIGHT),
    ) == {
        (5 + 1, 5 + 2),
        (5 + 2, 5 + 1),
        (5 + 2, 5 - 1),
        (5 + 1, 5 - 2),
        (5 - 1, 5 - 2),
        (5 - 2, 5 - 1),
        (5 - 2, 5 + 1),
        (5 - 1, 5 + 2),
    }


def test_get_squares_knight_obstructed():
    position = Position()
    position.add(Piece(WHITE, BISHOP), (1, 3))
    position.add(Piece(BLACK, PAWN), (2, 2))

    assert get_squares(
        current_square=Square(0, 1),
        position=position,
        piece=Piece(WHITE, KNIGHT),
    ) == {
        (2, 0),  # empty square
        (2, 2),  # enemy pawn
    }


def test_bishop_moves():
    position = Position(width=5, height=5)
    assert get_squares(
        current_square=Square(2, 2),
        position=position,
        piece=Piece(WHITE, BISHOP),
    ) == {
        (0, 0),
        (1, 1),
        (3, 3),
        (4, 4),
        (0, 4),
        (1, 3),
        (3, 1),
        (4, 0),
    }


def test_bishop_moves_obstructed():
    position = Position(width=5, height=5)
    position.add(Piece(BLACK, PAWN), (3, 3))
    position.add(Piece(WHITE, KING), (1, 1))
    assert get_squares(
        current_square=Square(2, 2),
        position=position,
        piece=Piece(WHITE, BISHOP),
    ) == {
        # (0, 0),  # behind king
        # (1, 1),  # occupied by king
        (3, 3),
        # (4, 4),  # behind pawn
        (0, 4),
        (1, 3),
        (3, 1),
        (4, 0),
    }


@pytest.mark.parametrize(
    "description, param",
    [
        (
            "white pawn on starting square has 2 moves",
            dict(starting_square=(0, 1), team=WHITE, expected_squares={(0, 2), (0, 3)}),
        ),
        (
            "white pawn on arbitrary square has 1 move",
            dict(starting_square=(6, 6), team=WHITE, expected_squares={(6, 7)}),
        ),
        (
            "white pawn on back rank can't move any further",
            dict(starting_square=(7, 7), team=WHITE, expected_squares=set()),
        ),
        (
            "black pawn on starting square has 2 moves",
            dict(starting_square=(0, 6), team=BLACK, expected_squares={(0, 5), (0, 4)}),
        ),
        (
            "black pawn on arbitrary square has 1 move",
            dict(starting_square=(0, 5), team=BLACK, expected_squares={(0, 4)}),
        ),
        (
            "black pawn on back rank can't move any further",
            dict(starting_square=(0, 0), team=BLACK, expected_squares=set()),
        ),
    ],
)
def test_pawn_moves_unobstructed(description, param):
    position = Position()
    assert (
        get_squares(
            current_square=param["starting_square"],
            position=position,
            piece=Piece(param["team"], PAWN),
        )
        == param["expected_squares"]
    )


@pytest.mark.parametrize(
    "description, param",
    [
        (
            "unobstructed white pawn on starting square has 2 moves",
            dict(
                starting_square=(0, 1),
                team=WHITE,
                expected_squares={(0, 2), (0, 3)},
            ),
        ),
        (
            "white pawn on starting square obstructed by piece on next square has no moves",
            dict(
                starting_square=(1, 1),
                team=WHITE,
                expected_squares=set(),
            ),
        ),
        (
            "white pawn on starting square obstructed by piece 2 squares away can only move 1 square",
            dict(
                starting_square=(2, 1),
                team=WHITE,
                expected_squares={(2, 2)},
            ),
        ),
        (
            "white pawn on arbitrary square has 1 move",
            dict(
                starting_square=(3, 2),
                team=WHITE,
                expected_squares={(3, 3)},
            ),
        ),
        (
            "white pawn on back rank has no moves",
            dict(
                starting_square=(4, 7),
                team=WHITE,
                expected_squares=set(),
            ),
        ),
        (
            "unobstructed black pawn on starting square has 2 moves",
            dict(
                starting_square=(0, 6),
                team=BLACK,
                expected_squares={(0, 5), (0, 4)},
            ),
        ),
        (
            "black pawn on starting square obstructed by piece on next square has no moves",
            dict(
                starting_square=(1, 6),
                team=BLACK,
                expected_squares=set(),
            ),
        ),
        (
            "black pawn on starting square obstructed by piece 2 squares away can only move 1 square",
            dict(
                starting_square=(2, 6),
                team=BLACK,
                expected_squares={(2, 5)},
            ),
        ),
        (
            "black pawn on arbitrary square has 1 move",
            dict(
                starting_square=(3, 5),
                team=BLACK,
                expected_squares={(3, 4)},
            ),
        ),
        (
            "black pawn on back rank has no moves",
            dict(
                starting_square=(4, 0),
                team=BLACK,
                expected_squares=set(),
            ),
        ),
    ],
)
def test_pawn_moves_obstructed(description, param):
    position = Position()
    position.add(Piece(WHITE, KING), (1, 2))  # obstructs white pawns on 1-file making ANY moves
    position.add(Piece(WHITE, KING), (2, 3))  # obstructs white pawns on 2-file a double move
    position.add(Piece(BLACK, KING), (1, 5))  # obstructs black pawns on 1-file making ANY moves
    position.add(Piece(BLACK, KING), (2, 4))  # obstructs black pawns on 2-file a double move
    assert (
        get_squares(
            current_square=param["starting_square"],
            position=position,
            piece=Piece(param["team"], PAWN),
        )
        == param["expected_squares"]
    )


@pytest.mark.parametrize(
    "description, param",
    [
        (
            "white pawn can capture 1 rook",
            dict(
                starting_square=(0, 1),
                team=WHITE,
                expected_squares={(0, 2), (0, 3), (1, 2)},
            ),
        ),
        (
            "white pawn can capture 2 rooks",
            dict(
                starting_square=(2, 1),
                team=WHITE,
                expected_squares={(2, 2), (2, 3), (1, 2), (3, 2)},
            ),
        ),
        (
            "black pawn can capture 1 rook",
            dict(
                starting_square=(0, 6),
                team=BLACK,
                expected_squares={(0, 5), (0, 4), (1, 5)},
            ),
        ),
        (
            "black pawn can capture 2 rooks",
            dict(
                starting_square=(2, 6),
                team=BLACK,
                expected_squares={(2, 5), (2, 4), (1, 5), (3, 5)},
            ),
        ),
    ],
)
def test_pawn_captures(description, param):
    position = Position()
    position.add(Piece(WHITE, ROOK), (1, 5))
    position.add(Piece(WHITE, ROOK), (3, 5))
    position.add(Piece(BLACK, ROOK), (1, 2))
    position.add(Piece(BLACK, ROOK), (3, 2))
    assert (
        get_squares(
            current_square=param["starting_square"],
            position=position,
            piece=Piece(param["team"], PAWN),
        )
        == param["expected_squares"]
    )


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
            "classic back rank",
            dict(
                position="/".join(
                    [
                        ".k..R...",
                        "ppp..ppp",
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
            "back rank except the king has a square",
            dict(
                position="/".join(
                    [
                        "..k.R...",
                        "ppp.....",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                    ]
                ),
                team=BLACK,
                expected_result=False,
            ),
        ),
        (
            "back rank except we can block it",
            dict(
                position="/".join(
                    [
                        "..k.R...",
                        "pppp....",
                        "........",
                        "......b.",
                        "........",
                        "........",
                        "........",
                        "........",
                    ]
                ),
                team=BLACK,
                expected_result=False,
            ),
        ),
        (
            "back rank except the king can capture",
            dict(
                position="/".join(
                    [
                        "...kR...",
                        "pppp....",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                    ]
                ),
                team=BLACK,
                expected_result=False,
            ),
        ),
        (
            "back rank except the piece can be captured",
            dict(
                position="/".join(
                    [
                        "k...R...",
                        "pppp....",
                        "........",
                        "........",
                        "........",
                        "....q...",
                        "........",
                        "........",
                    ]
                ),
                team=BLACK,
                expected_result=False,
            ),
        ),
        (
            "scholar's mate",
            dict(
                position="/".join(
                    [
                        "r.bqkbnr",
                        "pppp.Qpp",
                        "..n.....",
                        "....pp..",
                        "..B.P...",
                        "........",
                        "PPPP.PPP",
                        "RNB.K.NR",
                    ]
                ),
                team=BLACK,
                expected_result=True,
            ),
        ),
        (
            "the bishop can't block because it's pinned",
            dict(
                position="/".join(
                    [
                        "k.......",
                        ".b......",
                        "...B....",
                        "...Q....",
                        "........",
                        "RR......",
                        "........",
                        "........",
                    ]
                ),
                team=BLACK,
                expected_result=True,
            ),
        ),
    ],
)
def test_is_checkmated(description, params):
    position = Position()
    position.from_fen(params["position"])
    assert is_checkmated(params["team"], position) == params["expected_result"]
