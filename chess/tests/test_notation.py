import pytest

from chess.notation import parse_pgn_move


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

