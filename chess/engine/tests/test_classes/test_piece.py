import pytest

from chess.constants import WHITE, BLACK, PAWN, BISHOP, KING, QUEEN
from chess.engine.classes.piece import Piece


@pytest.mark.parametrize(
    "piece1, piece2, should_match",
    [
        (Piece(WHITE, PAWN), Piece(WHITE, PAWN), True),
        (Piece(WHITE, PAWN), Piece(BLACK, PAWN), False),
        (Piece(WHITE, PAWN), Piece(WHITE, PAWN), True),
        (Piece(BLACK, PAWN), Piece(BLACK, PAWN), True),
        (Piece(BLACK, PAWN), Piece(BLACK, BISHOP), False),
    ],
)
def test_piece__eq__(piece1, piece2, should_match):
    assert (piece1 == piece2) == should_match


@pytest.mark.parametrize(
    "piece_type, team, letter",
    [
        (KING, WHITE, "K"),
        (KING, BLACK, "k"),
        (QUEEN, WHITE, "Q"),
        (QUEEN, BLACK, "q"),
    ],
)
def test_piece_from_letter(piece_type, team, letter):
    piece = Piece.from_letter(letter)
    assert piece == Piece(team, piece_type)
