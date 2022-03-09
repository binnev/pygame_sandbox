import pytest

from chess.engine.classes.square import Square


@pytest.mark.parametrize(
    "string, expected_square",
    [
        ("a1", Square(0, 0)),
        ("h1", Square(7, 0)),
        ("h2", Square(7, 1)),
        ("h8", Square(7, 7)),
        ("a1", Square(0, 0)),
        ("d1", Square(3, 0)),
        ("a2", Square(0, 1)),
        ("d2", Square(3, 1)),
    ],
)
def test_square_from_str(string, expected_square):
    assert Square.from_str(string) == expected_square


@pytest.mark.parametrize(
    "square, expected_name",
    [
        (Square(0, 0), "a1"),
        (Square(3, 0), "d1"),
        (Square(0, 1), "a2"),
        (Square(3, 1), "d2"),
        (Square(0, 0), "a1"),
        (Square(7, 0), "h1"),
        (Square(7, 1), "h2"),
        (Square(7, 7), "h8"),
    ],
)
def test_square_to_str(square, expected_name):
    assert square.to_str() == expected_name
