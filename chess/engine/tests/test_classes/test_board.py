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



@pytest.mark.parametrize(
    "description, params",
    [
        (
            "starting position",
            dict(
                position="/".join(
                    [
                        "k.......",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "K.......",
                    ]
                ),
                team=WHITE,
                expected_result=[
                    ((0, 0), (0, 1)),
                    ((0, 0), (1, 0)),
                    ((0, 0), (1, 1)),
                ],
            ),
        ),
    ],
)
def test_chessboard_team_moves(description, params):
    board = ChessBoard()
    board.load_fen_position(params["position"])
    assert board.team_moves(params["team"]) == params["expected_result"]


@pytest.mark.parametrize(
    "description, params",
    [
        (
            "legal move",
            dict(
                position="/".join(
                    [
                        "k.......",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "K.......",
                    ]
                ),
                move=[(0, 0), (1, 0)],
                expected_result=True,
            ),
        ),
        (
            "square not on board",
            dict(
                position="/".join(
                    [
                        "k.......",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "K.......",
                    ]
                ),
                move=[(0, 0), (420, 69)],
                expected_result=False,
            ),
        ),
        (
            "move puts self in check",
            dict(
                position="/".join(
                    [
                        "q.......",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "B.......",
                        "K.......",
                    ]
                ),
                move=[(0, 1), (1, 2)],
                expected_result=False,
            ),
        ),
        (
            "move blocks a check",
            dict(
                position="/".join(
                    [
                        "q.......",
                        "........",
                        "........",
                        "........",
                        "........",
                        ".B......",
                        "........",
                        "K.......",
                    ]
                ),
                move=[(1, 2), (0, 1)],
                expected_result=True,
            ),
        ),
    ],
)
def test_chessboard_is_move_legal(description, params):
    board = ChessBoard()
    board.load_fen_position(params["position"])
    assert board.is_move_legal(params["move"]) == params["expected_result"]


@pytest.mark.parametrize(
    "description, params",
    [
        (
            "two kings",
            dict(
                position="/".join(
                    [
                        "k.......",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "K.......",
                    ]
                ),
                team=WHITE,
                expected_result=[
                    ((0, 0), (0, 1)),
                    ((0, 0), (1, 0)),
                    ((0, 0), (1, 1)),
                ],
            ),
        ),
        (
            "only the king can move because of the pin",
            dict(
                position="/".join(
                    [
                        "q.......",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "B.......",
                        "K.......",
                    ]
                ),
                team=WHITE,
                expected_result=[
                    ((0, 0), (1, 0)),
                    ((0, 0), (1, 1)),
                ],
            ),
        ),
        (
            "stalemate",
            dict(
                position="/".join(
                    [
                        "qr......",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "B.......",
                        "K.......",
                    ]
                ),
                team=WHITE,
                expected_result=[],
            ),
        ),
    ],
)
def test_chessboard_team_legal_moves(description, params):
    board = ChessBoard()
    board.load_fen_position(params["position"])
    assert board.team_legal_moves(params["team"]) == params["expected_result"]


@pytest.mark.parametrize(
    "description, params",
    [
        (
            "two kings",
            dict(
                position="/".join(
                    [
                        "k.......",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "K.......",
                    ]
                ),
                team=WHITE,
                expected_result=False,
            ),
        ),
        (
            "stalemate",
            dict(
                position="/".join(
                    [
                        "qr......",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "B.......",
                        "K.......",
                    ]
                ),
                team=WHITE,
                expected_result=True,
            ),
        ),
        (
            "king and queen stalemate",
            dict(
                position="/".join(
                    [
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "..q.k...",
                        "........",
                        "...K....",
                    ]
                ),
                team=WHITE,
                expected_result=True,
            ),
        ),
    ],
)
def test_chessboard_is_stalemated(description, params):
    board = ChessBoard()
    board.load_fen_position(params["position"])
    assert board.is_stalemated(params["team"]) == params["expected_result"]


def test_chessboard_piece_legal_moves():
    board = ChessBoard()
    board.load_fen_position(
        "/".join(
            [
                "........",
                "........",
                "........",
                "........",
                "........",
                "..q.k...",
                "........",
                "...K....",
            ]
        )
    )
    assert board.piece_legal_moves((3, 0)) == []
    black_king_moves = set(board.piece_legal_moves((4, 2)))
    expected = {
        ((4, 2), (3, 2)),  # left
        ((4, 2), (5, 2)),  # right
        ((4, 2), (4, 3)),  # up
        ((4, 2), (5, 3)),  # right up
        ((4, 2), (3, 3)),  # left up
        ((4, 2), (5, 1)),  # right down
    }
    assert black_king_moves.difference(expected) == expected.difference(black_king_moves) == set()
