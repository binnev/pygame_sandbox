import pytest

from chess.engine.classes import WHITE, King, BLACK, Queen


@pytest.mark.parametrize(
    "piece_class, team, expected_str",
    [
        (King, WHITE, "K"),
        (King, BLACK, "k"),
        (Queen, WHITE, "Q"),
        (Queen, BLACK, "q"),
    ],
)
def test_piece_str(piece_class, team, expected_str):
    piece = piece_class(team)
    assert str(piece) == expected_str
