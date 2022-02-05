import pytest

from chess.constants import BLACK, WHITE
from chess.engine.classes.piece import Pawn, King, Queen, Rook
from chess.notation import parse_pgn_move, parse_fen_position, parse_fen_row


@pytest.mark.parametrize(
    "string, piece, specifier, capture, target",
    [
        ("e4", "P", None, None, "e4"),
        ("dxe4", "P", "d", "x", "e4"),
        ("Re4", "R", None, None, "e4"),
        ("Rae4", "R", "a", None, "e4"),
        ("Rxe4", "R", None, "x", "e4"),
        ("Rbxe4", "R", "b", "x", "e4"),
        ("R5xe4", "R", "5", "x", "e4"),
    ],
)
def test_parse_pgn_move(string, piece, specifier, capture, target):
    p, s, c, t = parse_pgn_move(string)
    assert p == piece
    assert s == specifier
    assert c == capture
    assert t == target


@pytest.mark.parametrize(
    "string, expected_pieces",
    [
        ("8", [None] * 8),  # 8 empty spaces,
        ("p", [Pawn(BLACK)]),
        ("p2P", [Pawn(BLACK), None, None, Pawn(WHITE)]),
        ("KkQq", [King(WHITE), King(BLACK), Queen(WHITE), Queen(BLACK)]),
    ],
)
def test_parse_fen_row(string, expected_pieces):
    assert parse_fen_row(string) == expected_pieces


@pytest.mark.parametrize(
    "string, expected_pieces",
    [
        ("8/8/8/8/8/8/8/R7 w KQkq - 0 1", {(0, 0): Rook(WHITE)}),
        ("8/8/8/8/8/8/8/7R w KQkq - 0 1", {(7, 0): Rook(WHITE)}),
        ("8/3r4/8/8/8/8/8/8 w KQkq - 0 1", {(3, 6): Rook(BLACK)}),
        ("7K/8/8/8/8/8/8/q7 w KQkq - 0 1", {(7, 7): King(WHITE), (0, 0): Queen(BLACK)}),
    ],
)
def test_parse_fen_position(string, expected_pieces):
    pieces, _ = parse_fen_position(string)
    assert pieces == expected_pieces
