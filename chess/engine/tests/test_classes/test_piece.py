import pytest

from chess.constants import WHITE, BLACK
from chess.engine.classes.board import ChessBoard


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


def test_piece__repr__():

    piece = Pawn(BLACK)
    assert piece.__repr__() == "black Pawn"

    board = ChessBoard()
    board.add_piece(piece, (4, 6))
    assert piece.__repr__() == "black Pawn on e7"


@pytest.mark.parametrize(
    "piece1, piece2, should_match",
    [
        (Pawn(), Pawn(), True),
        (Pawn(WHITE), Pawn(BLACK), False),
        (Pawn(WHITE), Pawn(WHITE), True),
        (Pawn(BLACK), Pawn(BLACK), True),
        (Pawn(BLACK), Bishop(BLACK), False),
    ],
)
def test_piece__eq__(piece1, piece2, should_match):
    assert (piece1 == piece2) == should_match


@pytest.mark.parametrize(
    "piece_class, team, letter",
    [
        (King, WHITE, "K"),
        (King, BLACK, "k"),
        (Queen, WHITE, "Q"),
        (Queen, BLACK, "q"),
    ],
)
def test_piece_from_letter(piece_class, team, letter):
    piece = Piece.from_letter(letter)
    assert piece == piece_class(team=team)
