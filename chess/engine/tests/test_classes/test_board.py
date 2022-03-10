import pytest

from chess.constants import WHITE, BLACK, KING, PAWN, QUEEN, ROOK
from chess.engine.classes.board import ChessBoard, Square
from chess.engine.classes.piece import Piece


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
    board.position.add(Piece(WHITE, PAWN), (0, 0))
    board.position.add(Piece(WHITE, PAWN), (1, 1))
    board.position.add(Piece(WHITE, PAWN), (2, 2))
    board.position.add(Piece(WHITE, PAWN), (3, 3))
    board.position.add(Piece(WHITE, PAWN), (4, 4))
    board.position.add(Piece(WHITE, QUEEN), (0, 7))
    board.position.add(Piece(WHITE, KING), (7, 0))
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
    assert board1.position == board2.position
    rook = board1.position[(0, 0)]
    assert rook.type == ROOK


def test_fen_position():
    board = ChessBoard()
    board.load_standard_setup()
    assert board.fen_position == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"


@pytest.mark.parametrize(
    "description, params",
    [
        (
            "white knight moves from starting position",
            dict(
                starting_position="/".join(
                    [
                        "rnbqkbnr",
                        "pppppppp",
                        "........",
                        "........",
                        "........",
                        "........",
                        "PPPPPPPP",
                        "RNBQKBNR",
                    ]
                ),
                move="Nf3",
                player=WHITE,
                final_position="/".join(
                    [
                        "rnbqkbnr",
                        "pppppppp",
                        "........",
                        "........",
                        "........",
                        ".....N..",
                        "PPPPPPPP",
                        "RNBQKB.R",
                    ]
                ),
            ),
        ),
        (
            "black knight moves after white's first knight move",
            dict(
                starting_position="/".join(
                    [
                        "rnbqkbnr",
                        "pppppppp",
                        "........",
                        "........",
                        "........",
                        ".....N..",
                        "PPPPPPPP",
                        "RNBQKB.R",
                    ]
                ),
                move="Nf6",
                player=BLACK,
                final_position="/".join(
                    [
                        "rnbqkb.r",
                        "pppppppp",
                        ".....n..",
                        "........",
                        "........",
                        ".....N..",
                        "PPPPPPPP",
                        "RNBQKB.R",
                    ]
                ),
            ),
        ),
        (
            "black rook moves to e4",
            dict(
                starting_position="/".join(
                    [
                        "........",
                        "........",
                        "........",
                        "....r...",
                        "........",
                        "....R...",
                        "........",
                        "........",
                    ]
                ),
                move="Re4",
                player=BLACK,
                final_position="/".join(
                    [
                        "........",
                        "........",
                        "........",
                        "........",
                        "....r...",
                        "....R...",
                        "........",
                        "........",
                    ]
                ),
            ),
        ),
        (
            "white rook moves to e4",
            dict(
                starting_position="/".join(
                    [
                        "........",
                        "........",
                        "........",
                        "....r...",
                        "........",
                        "....R...",
                        "........",
                        "........",
                    ]
                ),
                move="Re4",
                player=WHITE,
                final_position="/".join(
                    [
                        "........",
                        "........",
                        "........",
                        "....r...",
                        "....R...",
                        "........",
                        "........",
                        "........",
                    ]
                ),
            ),
        ),
        (
            "rook 1 moves to e4",
            dict(
                starting_position="/".join(
                    [
                        "....R...",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "....R...",
                    ]
                ),
                move="R1e4",
                player=WHITE,
                final_position="/".join(
                    [
                        "....R...",
                        "........",
                        "........",
                        "........",
                        "....R...",
                        "........",
                        "........",
                        "........",
                    ]
                ),
            ),
        ),
        (
            "rook 8 to e4",
            dict(
                starting_position="/".join(
                    [
                        "....R...",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "....R...",
                    ]
                ),
                move="R8e4",
                player=WHITE,
                final_position="/".join(
                    [
                        "........",
                        "........",
                        "........",
                        "........",
                        "....R...",
                        "........",
                        "........",
                        "....R...",
                    ]
                ),
            ),
        ),
        (
            "knight 1 moves",
            dict(
                starting_position="/".join(
                    [
                        "........",
                        "........",
                        "........",
                        "..N.....",
                        "........",
                        "........",
                        "........",
                        "N.......",
                    ]
                ),
                move="N1b3",
                player=WHITE,
                final_position="/".join(
                    [
                        "........",
                        "........",
                        "........",
                        "..N.....",
                        "........",
                        ".N......",
                        "........",
                        "........",
                    ]
                ),
            ),
        ),
        (
            "knight a moves",
            dict(
                starting_position="/".join(
                    [
                        "........",
                        "........",
                        "........",
                        "..N.....",
                        "........",
                        "........",
                        "........",
                        "N.......",
                    ]
                ),
                move="Nab3",
                player=WHITE,
                final_position="/".join(
                    [
                        "........",
                        "........",
                        "........",
                        "..N.....",
                        "........",
                        ".N......",
                        "........",
                        "........",
                    ]
                ),
            ),
        ),
        (
            "knight 5 moves",
            dict(
                starting_position="/".join(
                    [
                        "........",
                        "........",
                        "........",
                        "..N.....",
                        "........",
                        "........",
                        "........",
                        "N.......",
                    ]
                ),
                move="N5b3",
                player=WHITE,
                final_position="/".join(
                    [
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        ".N......",
                        "........",
                        "N.......",
                    ]
                ),
            ),
        ),
        (
            "knight c moves",
            dict(
                starting_position="/".join(
                    [
                        "........",
                        "........",
                        "........",
                        "..N.....",
                        "........",
                        "........",
                        "........",
                        "N.......",
                    ]
                ),
                move="Ncb3",
                player=WHITE,
                final_position="/".join(
                    [
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        ".N......",
                        "........",
                        "N.......",
                    ]
                ),
            ),
        ),
    ],
)
def test_do_pgn_move(description, params):
    board = ChessBoard()  # todo: set current player in FEN string
    board.load_fen_position(params["starting_position"])
    board.active_team = params["player"]
    board.do_pgn_move(params["move"])
    assert board.position.__str__(V_SEP="/", H_SEP="") == params["final_position"]
