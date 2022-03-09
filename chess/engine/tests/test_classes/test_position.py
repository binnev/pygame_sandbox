from chess.constants import WHITE, KING, BLACK
from chess.engine.classes.piece import Piece
from chess.engine.classes.position import Position
from chess.engine.classes.square import Square


def test_squares():
    position = Position(width=2, height=2)
    assert position.squares == ((0, 0), (1, 0), (0, 1), (1, 1))


def test_add():
    position = Position()
    king = Piece(WHITE, KING)
    position.add(king, (2, 4))
    assert position.get((2, 4)) is king


def test_add_plays_nice_with_square_namedtuple():
    position = Position()
    king = Piece(WHITE, KING)
    position.add(king, (2, 4))
    assert position[(2, 4)] == king
    assert position[Square(2, 4)] == king

    position.add(king, Square(2, 4))
    assert len(position) == 1
    assert position[(2, 4)] == king
    assert position[Square(2, 4)] == king


def test_pawn_starting_squares():
    position = Position()
    assert position.pawn_starting_squares(WHITE) == {
        Square(0, 1),
        Square(1, 1),
        Square(2, 1),
        Square(3, 1),
        Square(4, 1),
        Square(5, 1),
        Square(6, 1),
        Square(7, 1),
    }

    assert position.pawn_starting_squares(BLACK) == {
        Square(0, 6),
        Square(1, 6),
        Square(2, 6),
        Square(3, 6),
        Square(4, 6),
        Square(5, 6),
        Square(6, 6),
        Square(7, 6),
    }
