import pytest

from chess.engine.classes.board import ChessBoard
from chess.engine.classes.piece import King, Pawn, Queen
from chess.constants import WHITE, BLACK


def test_chessboard_square_coords():
    board = ChessBoard(8, 8)
    assert board.square_coords("a1") == (0, 0)
    assert board.square_coords("h1") == (7, 0)
    assert board.square_coords("h2") == (7, 1)
    assert board.square_coords("h8") == (7, 7)
    assert board.square_name((0, 0)) == "a1"
    assert board.square_name((7, 0)) == "h1"
    assert board.square_name((7, 1)) == "h2"
    assert board.square_name((7, 7)) == "h8"

    board = ChessBoard(2, 4)
    assert board.square_coords("a1") == (0, 0)
    assert board.square_coords("d1") == (3, 0)
    assert board.square_coords("a2") == (0, 1)
    assert board.square_coords("d2") == (3, 1)
    assert board.square_name((0, 0)) == "a1"
    assert board.square_name((3, 0)) == "d1"
    assert board.square_name((0, 1)) == "a2"
    assert board.square_name((3, 1)) == "d2"


def test_chessboard_locate():
    board = ChessBoard()
    king1 = King(WHITE)
    king2 = King(WHITE)
    king3 = King(BLACK)
    board.add_piece(king1, (1, 1))
    board.add_piece(king2, (2, 2))
    board.add_piece(king3, (3, 3))

    assert board.locate(king1) == (1, 1)
    assert board.locate(king2) == (2, 2)
    assert board.locate(king3) == (3, 3)


def test_chessboard_squares():
    board = ChessBoard(2, 2)
    assert board.squares == ((0, 0), (1, 0), (0, 1), (1, 1))


def test_chessboard_add_piece():
    board = ChessBoard()
    king = King(WHITE)
    board.add_piece(king, (2, 4))
    assert board.contents[(2, 4)] is king
    assert king.board == board


def test_str_empty():
    board = ChessBoard()
    assert str(board) == "\n".join(
        [
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
        ]
    )


def test_str_populated():
    board = ChessBoard()
    board.add_piece(Pawn(), (0, 0))
    board.add_piece(Pawn(), (1, 1))
    board.add_piece(Pawn(), (2, 2))
    board.add_piece(Pawn(), (3, 3))
    board.add_piece(Pawn(), (4, 4))
    board.add_piece(Queen(), (0, 7))
    board.add_piece(King(), (7, 0))
    assert str(board) == "\n".join(
        [
            "Q . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . P . . .",
            ". . . P . . . .",
            ". . P . . . . .",
            ". P . . . . . .",
            "P . . . . . . K",
        ]
    )


def test_str_load_standard_setup():
    board = ChessBoard()
    board.load_standard_setup()
    assert str(board) == "\n".join(
        [
            "r n b q k b n r",
            "p p p p p p p p",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            "P P P P P P P P",
            "R N B Q K B N R",
        ]
    )


def test_load_fen_position():
    board1 = ChessBoard()
    board1.load_standard_setup()
    board2 = ChessBoard()
    board2.load_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    assert board1.contents == board2.contents


def test_fen_position():
    board = ChessBoard()
    board.load_standard_setup()
    assert board.fen_position == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"


# @pytest.mark.parametrize(
#     "starting_position, move, final_position"[
#         (
#             "/".join(
#                 [
#                     "rnbqkbnr",
#                     "pppppppp",
#                     "8",
#                     "8",
#                     "8",
#                     "8",
#                     "PPPPPPPP",
#                     "RNBQKBNR",
#                 ]
#             ),
#             "Nf3",
#             WHITE,
#             "/".join(
#                 [
#                     "rnbqkbnr",
#                     "pppppppp",
#                     "8",
#                     "8",
#                     "8",
#                     "5N2",
#                     "PPPPPPPP",
#                     "RNBQKB1R",
#                 ]
#             ),
#         )
#     ]
# )
# def test_do_pgn_move(starting_position, move, final_position):
#     board = ChessBoard()  # todo: set current player in FEN string
#     board.load_fen_position(starting_position)
#     board.do_pgn_move(move)
#     assert board.fen_position == final_position


# todo: Move class. Will be like a diff between positions
#  - stack of Moves to record history and allow undoing
#  - tree with branches to allow analysis
#  - Move.apply/undo to move up/down the stack
#  - parser for "rbxa4" type moves (again, Move.to/from_string)
