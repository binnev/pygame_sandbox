import pytest

from chess.constants import BLACK, WHITE, PAWN, ROOK, KING, QUEEN
from chess.engine.classes.piece import Piece
from chess.notation import (
    parse_pgn_move,
    parse_fen_position,
    parse_fen_row,
    generate_fen_row,
    generate_fen_position,
    parse_fen_string,
)


@pytest.mark.parametrize(
    "string, piece, specifier, capture, target",
    [
        ("e4", PAWN, None, None, "e4"),
        ("dxe4", PAWN, "d", "x", "e4"),
        ("Re4", ROOK, None, None, "e4"),
        ("Rae4", ROOK, "a", None, "e4"),
        ("Rxe4", ROOK, None, "x", "e4"),
        ("Rbxe4", ROOK, "b", "x", "e4"),
        ("R5xe4", ROOK, "5", "x", "e4"),
    ],
)
def test_parse_pgn_move(string, piece, specifier, capture, target):
    p, s, c, t = parse_pgn_move(string)
    assert p == piece
    assert s == specifier
    assert c == capture
    assert t == target


FEN_ROW_PIECES = [
    ("8", [None] * 8),  # 8 empty spaces,
    ("p", [Piece(BLACK, PAWN)]),
    ("p2P", [Piece(BLACK, PAWN), None, None, Piece(WHITE, PAWN)]),
    ("KkQq", [Piece(WHITE, KING), Piece(BLACK, KING), Piece(WHITE, QUEEN), Piece(BLACK, QUEEN)]),
    (
        "KkQq3",
        [
            Piece(WHITE, KING),
            Piece(BLACK, KING),
            Piece(WHITE, QUEEN),
            Piece(BLACK, QUEEN),
            None,
            None,
            None,
        ],
    ),
]


@pytest.mark.parametrize("string, pieces", FEN_ROW_PIECES)
def test_parse_fen_row(string, pieces):
    assert parse_fen_row(string) == pieces


@pytest.mark.parametrize("string, pieces", FEN_ROW_PIECES)
def test_generate_fen_row(string, pieces):
    assert generate_fen_row(pieces) == string


@pytest.mark.parametrize(
    "string, expected_outputs",
    [
        ("8/8/8/8/8/8/8/R7 w KQkq - 0 1", ("8/8/8/8/8/8/8/R7", "w", "KQkq", "-", "0", "1")),
        ("8/8/8/8/8/8/8/7R w KQkq - 0 1", ("8/8/8/8/8/8/8/7R", "w", "KQkq", "-", "0", "1")),
        ("8/3r4/8/8/8/8/8/8 w KQkq - 0 1", ("8/3r4/8/8/8/8/8/8", "w", "KQkq", "-", "0", "1")),
        ("7K/8/8/8/8/8/8/q7 w KQkq - 0 1", ("7K/8/8/8/8/8/8/q7", "w", "KQkq", "-", "0", "1")),
        (
            ".......K/......../......../......../......../......../......../q....... w KQkq - 0 1",
            (
                ".......K/......../......../......../......../......../......../q.......",
                "w",
                "KQkq",
                "-",
                "0",
                "1",
            ),
        ),
        (
            ".......K/......../......../......../......../......../......../q.......",
            (
                ".......K/......../......../......../......../......../......../q.......",
                None,
                None,
                None,
                None,
                None,
            ),
        ),
    ],
)
def test_parse_fen_string(string, expected_outputs):
    assert parse_fen_string(string) == expected_outputs


FEN_POSITION_PIECES = [
    ("8/8/8/8/8/8/8/R7", {(0, 0): Piece(WHITE, ROOK)}),
    ("8/8/8/8/8/8/8/7R", {(7, 0): Piece(WHITE, ROOK)}),
    ("8/3r4/8/8/8/8/8/8", {(3, 6): Piece(BLACK, ROOK)}),
    ("7K/8/8/8/8/8/8/q7", {(7, 7): Piece(WHITE, KING), (0, 0): Piece(BLACK, QUEEN)}),
]


@pytest.mark.parametrize("string, pieces", FEN_POSITION_PIECES)
def test_parse_fen_position(string, pieces):
    assert parse_fen_position(string) == pieces


@pytest.mark.parametrize("string, pieces", FEN_POSITION_PIECES)
def test_generate_fen_position(string, pieces):
    assert generate_fen_position(pieces) == string


@pytest.mark.parametrize(
    "string, pieces",
    [
        ("7K/8/8/8/8/8/8/q7", {(7, 7): Piece(WHITE, KING), (0, 0): Piece(BLACK, QUEEN)}),
        (
            "/".join(
                [
                    ".......K",
                    "........",
                    "........",
                    "........",
                    "........",
                    "........",
                    "........",
                    "q.......",
                ]
            ),
            {(7, 7): Piece(WHITE, KING), (0, 0): Piece(BLACK, QUEEN)},
        ),
    ],
)
def test_parse_fen_position_can_handle_dots_for_testing_purposes(string, pieces):
    assert parse_fen_position(string) == pieces
