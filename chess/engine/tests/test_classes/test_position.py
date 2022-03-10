from chess.constants import WHITE, KING, BLACK, QUEEN
from chess.engine.classes.piece import Piece
from chess.engine.classes.position import Position
from chess.engine.classes.square import Square


def test_init_empty():
    position = Position()
    assert len(position) == 0


def test_init_from_dict_literal():
    position = Position(
        {
            Square(0, 0): Piece(WHITE, KING),
            Square(0, 1): Piece(BLACK, QUEEN),
        }
    )
    assert len(position) == 2


def test_init_from_other_position():
    position1 = Position(
        {
            Square(0, 0): Piece(WHITE, KING),
            Square(0, 1): Piece(BLACK, QUEEN),
        }
    )
    position2 = Position(position1)
    assert position1 == position2
    assert len(position1) == len(position2) == 2
    # should be separate instances, not two links to the same data
    assert position2.pop((0, 0)) == Piece(WHITE, KING)
    assert position1 != position2
    assert len(position2) == 1


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
