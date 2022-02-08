import pytest

from chess.constants import WHITE, BLACK
from chess.engine.classes.board import ChessBoard
from chess.engine.classes.piece import King, Queen, Pawn, Bishop, Knight, Piece, Rook


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


@pytest.mark.parametrize(
    "description, param",
    [
        (
            "white pawn on starting square has 2 moves",
            dict(starting_square=(0, 1), team=WHITE, expected_moves={(0, 2), (0, 3)}),
        ),
        (
            "white pawn on arbitrary square has 1 move",
            dict(starting_square=(6, 6), team=WHITE, expected_moves={(6, 7)}),
        ),
        (
            "white pawn on back rank can't move any further",
            dict(starting_square=(7, 7), team=WHITE, expected_moves=set()),
        ),
        (
            "black pawn on starting square has 2 moves",
            dict(starting_square=(0, 6), team=BLACK, expected_moves={(0, 5), (0, 4)}),
        ),
        (
            "black pawn on arbitrary square has 1 move",
            dict(starting_square=(0, 5), team=BLACK, expected_moves={(0, 4)}),
        ),
        (
            "black pawn on back rank can't move any further",
            dict(starting_square=(0, 0), team=BLACK, expected_moves=set()),
        ),
    ],
)
def test_pawn_moves_unobstructed(description, param):
    board = ChessBoard()

    pawn = Pawn(param["team"])
    board.add_piece(pawn, param["starting_square"])
    assert pawn.moves == param["expected_moves"]


@pytest.mark.parametrize(
    "description, param",
    [
        (
            "unobstructed white pawn on starting square has 2 moves",
            dict(
                starting_square=(0, 1),
                team=WHITE,
                expected_moves={(0, 2), (0, 3)},
            ),
        ),
        (
            "white pawn on starting square obstructed by piece on next square has no moves",
            dict(
                starting_square=(1, 1),
                team=WHITE,
                expected_moves=set(),
            ),
        ),
        (
            "white pawn on starting square obstructed by piece 2 squares away can only move 1 square",
            dict(
                starting_square=(2, 1),
                team=WHITE,
                expected_moves={(2, 2)},
            ),
        ),
        (
            "white pawn on arbitrary square has 1 move",
            dict(
                starting_square=(3, 2),
                team=WHITE,
                expected_moves={(3, 3)},
            ),
        ),
        (
            "white pawn on back rank has no moves",
            dict(
                starting_square=(4, 7),
                team=WHITE,
                expected_moves=set(),
            ),
        ),
        (
            "unobstructed black pawn on starting square has 2 moves",
            dict(
                starting_square=(0, 6),
                team=BLACK,
                expected_moves={(0, 5), (0, 4)},
            ),
        ),
        (
            "black pawn on starting square obstructed by piece on next square has no moves",
            dict(
                starting_square=(1, 6),
                team=BLACK,
                expected_moves=set(),
            ),
        ),
        (
            "black pawn on starting square obstructed by piece 2 squares away can only move 1 square",
            dict(
                starting_square=(2, 6),
                team=BLACK,
                expected_moves={(2, 5)},
            ),
        ),
        (
            "black pawn on arbitrary square has 1 move",
            dict(
                starting_square=(3, 5),
                team=BLACK,
                expected_moves={(3, 4)},
            ),
        ),
        (
            "black pawn on back rank has no moves",
            dict(
                starting_square=(4, 0),
                team=BLACK,
                expected_moves=set(),
            ),
        ),
    ],
)
def test_pawn_moves_obstructed(description, param):
    board = ChessBoard()
    board.add_piece(King(), (1, 2))  # obstructs white pawns on 1-file making ANY moves
    board.add_piece(King(), (2, 3))  # obstructs white pawns on 2-file a double move
    board.add_piece(King(BLACK), (1, 5))  # obstructs black pawns on 1-file making ANY moves
    board.add_piece(King(BLACK), (2, 4))  # obstructs black pawns on 2-file a double move

    pawn = Pawn(param["team"])
    board.add_piece(pawn, param["starting_square"])
    assert pawn.moves == param["expected_moves"]


@pytest.mark.parametrize(
    "description, param",
    [
        (
            "white pawn can capture 1 rook",
            dict(
                starting_square=(0, 1),
                team=WHITE,
                expected_moves={(0, 2), (0, 3), (1, 2)},
            ),
        ),
        (
            "white pawn can capture 2 rooks",
            dict(
                starting_square=(2, 1),
                team=WHITE,
                expected_moves={(2, 2), (2, 3), (1, 2), (3, 2)},
            ),
        ),
        (
            "black pawn can capture 1 rook",
            dict(
                starting_square=(0, 6),
                team=BLACK,
                expected_moves={(0, 5), (0, 4), (1, 5)},
            ),
        ),
        (
            "black pawn can capture 2 rooks",
            dict(
                starting_square=(2, 6),
                team=BLACK,
                expected_moves={(2, 5), (2, 4), (1, 5), (3, 5)},
            ),
        ),
    ],
)
def test_pawn_captures(description, param):
    board = ChessBoard()
    board.add_piece(Rook(), (1, 5))
    board.add_piece(Rook(), (3, 5))
    board.add_piece(Rook(BLACK), (1, 2))
    board.add_piece(Rook(BLACK), (3, 2))

    pawn = Pawn(param["team"])
    board.add_piece(pawn, param["starting_square"])
    assert pawn.moves == param["expected_moves"]


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
