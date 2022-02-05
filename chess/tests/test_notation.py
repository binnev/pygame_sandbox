import pytest

from chess.engine.classes import BLACK, Pawn, WHITE, King, Queen
from chess.notation import parse_pgn_move, parse_fen_position, EMPTY, parse_fen_row


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
        ("8", [EMPTY] * 8),  # 8 empty spaces,
        ("p", [Pawn(BLACK)]),
        ("p2P", [Pawn(BLACK), EMPTY, EMPTY, Pawn(WHITE)]),
        ("KkQq", [King(WHITE), King(BLACK), Queen(WHITE), Queen(BLACK)]),
    ],
)
def test_parse_fen_row(string, expected_pieces):
    assert parse_fen_row(string) == expected_pieces


# @pytest.mark.parametrize("string", ["8/8/8/8/8/8/8/R7 w KQkq - 0 1"])
# def test_parse_fen_position(string):
#     position, _ = parse_fen_position(string)
#     assert position == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
