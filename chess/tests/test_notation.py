import pytest

from chess.constants import BLACK, WHITE
from chess.engine.classes.piece import Pawn, King, Queen, Rook
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
        ("e4", Pawn, None, None, "e4"),
        ("dxe4", Pawn, "d", "x", "e4"),
        ("Re4", Rook, None, None, "e4"),
        ("Rae4", Rook, "a", None, "e4"),
        ("Rxe4", Rook, None, "x", "e4"),
        ("Rbxe4", Rook, "b", "x", "e4"),
        ("R5xe4", Rook, "5", "x", "e4"),
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
    ("p", [Pawn(BLACK)]),
    ("p2P", [Pawn(BLACK), None, None, Pawn(WHITE)]),
    ("KkQq", [King(WHITE), King(BLACK), Queen(WHITE), Queen(BLACK)]),
    ("KkQq3", [King(WHITE), King(BLACK), Queen(WHITE), Queen(BLACK), None, None, None]),
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
    ],
)
def test_parse_fen_string(string, expected_outputs):
    assert parse_fen_string(string) == expected_outputs


FEN_POSITION_PIECES = [
    ("8/8/8/8/8/8/8/R7", {(0, 0): Rook(WHITE)}),
    ("8/8/8/8/8/8/8/7R", {(7, 0): Rook(WHITE)}),
    ("8/3r4/8/8/8/8/8/8", {(3, 6): Rook(BLACK)}),
    ("7K/8/8/8/8/8/8/q7", {(7, 7): King(WHITE), (0, 0): Queen(BLACK)}),
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
        ("7K/8/8/8/8/8/8/q7", {(7, 7): King(WHITE), (0, 0): Queen(BLACK)}),
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
            {(7, 7): King(WHITE), (0, 0): Queen(BLACK)},
        ),
    ],
)
def test_parse_fen_position_can_handle_dots_for_testing_purposes(string, pieces):
    assert parse_fen_position(string) == pieces
