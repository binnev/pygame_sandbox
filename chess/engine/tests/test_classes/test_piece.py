import pytest

from chess.engine.classes import WHITE, King, BLACK, Queen, ChessBoard, Knight, Pawn, Bishop


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


def test_king_moves():
    board = ChessBoard(4, 4)
    king = King()
    board.add_piece(king, (1, 1))

    assert king.moves == {
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 2),
        (2, 0),
        (2, 1),
        (2, 2),
    }


def test_king_moves_obstructed():
    board = ChessBoard(4, 4)
    king = King(WHITE)
    board.add_piece(king, (0, 0))
    board.add_piece(Pawn(WHITE), (1, 1))
    board.add_piece(Bishop(BLACK), (0, 1))

    assert king.moves == {
        (0, 1),  # enemy bishop
        (1, 0),  # empty square
    }


def test_knight_moves():
    board = ChessBoard()
    knight = Knight()
    board.add_piece(knight, (5, 5))
    assert knight.moves == {
        (5 + 1, 5 + 2),
        (5 + 2, 5 + 1),
        (5 + 2, 5 - 1),
        (5 + 1, 5 - 2),
        (5 - 1, 5 - 2),
        (5 - 2, 5 - 1),
        (5 - 2, 5 + 1),
        (5 - 1, 5 + 2),
    }


def test_knight_moves_obstructed():
    board = ChessBoard(4, 4)
    knight = Knight(WHITE)
    board.add_piece(knight, (0, 1))
    board.add_piece(Bishop(WHITE), (1, 3))
    board.add_piece(Pawn(BLACK), (2, 2))

    assert knight.moves == {
        (2, 0),  # empty square
        (2, 2),  # enemy pawn
    }


def test_bishop_moves():
    board = ChessBoard(5, 5)
    bishop = Bishop()
    board.add_piece(bishop, (2, 2))
    assert bishop.moves == {
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
    board = ChessBoard(5, 5)
    bishop = Bishop(WHITE)
    pawn = Pawn(BLACK)
    king = King(WHITE)
    board.add_piece(bishop, (2, 2))
    board.add_piece(pawn, (3, 3))
    board.add_piece(king, (1, 1))
    assert bishop.moves == {
        # (0, 0),  # behind king
        # (1, 1),  # occupied by king
        (3, 3),
        # (4, 4),  # behind pawn
        (0, 4),
        (1, 3),
        (3, 1),
        (4, 0),
    }
