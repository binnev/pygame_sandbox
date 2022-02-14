import pytest

from chess.constants import WHITE, BLACK
from chess.engine.classes.board import ChessBoard, Square
from chess.engine.classes.piece import King, Pawn, Queen, Rook


def test_square_coords():
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


def test_locate():
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


def test_squares():
    board = ChessBoard(2, 2)
    assert board.squares == ((0, 0), (1, 0), (0, 1), (1, 1))


def test_add_piece():
    board = ChessBoard()
    king = King(WHITE)
    board.add_piece(king, (2, 4))
    assert board.contents[(2, 4)] is king
    assert king.board == board


def test_add_piece_plays_nice_with_square_namedtuple():
    board = ChessBoard()
    king = King(WHITE)
    board.add_piece(king, (2, 4))
    assert board.contents[(2, 4)] == king
    assert board.contents[Square(2, 4)] == king

    board.add_piece(king, Square(2, 4))
    assert len(board.contents) == 1
    assert board.contents[(2, 4)] == king
    assert board.contents[Square(2, 4)] == king


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

    rook = board1.contents[(0, 0)]
    assert isinstance(rook, Rook)
    assert rook.board is board1  # check piece has link to parent board


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
    board.current_player = params["player"]
    board.do_pgn_move(params["move"])
    assert board.__str__(V_SEP="/", H_SEP="") == params["final_position"]


def test_pawn_starting_squares():
    board = ChessBoard()
    assert board.pawn_starting_squares(WHITE) == [
        (0, 1),
        (1, 1),
        (2, 1),
        (3, 1),
        (4, 1),
        (5, 1),
        (6, 1),
        (7, 1),
    ]

    assert board.pawn_starting_squares(BLACK) == [
        (0, 6),
        (1, 6),
        (2, 6),
        (3, 6),
        (4, 6),
        (5, 6),
        (6, 6),
        (7, 6),
    ]


@pytest.mark.parametrize(
    "description, params",
    [
        (
            "starting position",
            dict(
                position="/".join(
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
                team=WHITE,
                expected_result=False,
            ),
        ),
        (
            "with pawn",
            dict(
                position="/".join(
                    [
                        "....k...",
                        "...P....",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                    ]
                ),
                team=BLACK,
                expected_result=True,
            ),
        ),
        (
            "with bishop",
            dict(
                position="/".join(
                    [
                        "........",
                        "........",
                        "........",
                        "........",
                        ".....b..",
                        "........",
                        "...K....",
                        "........",
                    ]
                ),
                team=WHITE,
                expected_result=True,
            ),
        ),
        (
            "with bishop and rook",
            dict(
                position="/".join(
                    [
                        "........",
                        "...r....",
                        "........",
                        "........",
                        ".....b..",
                        "........",
                        "...K....",
                        "........",
                    ]
                ),
                team=WHITE,
                expected_result=True,
            ),
        ),
        (
            "with rook",
            dict(
                position="/".join(
                    [
                        "........",
                        "...r....",
                        "........",
                        "........",
                        "........",
                        "........",
                        "...K....",
                        "........",
                    ]
                ),
                team=WHITE,
                expected_result=True,
            ),
        ),
        (
            "with queen",
            dict(
                position="/".join(
                    [
                        ".......k",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "Q.......",
                    ]
                ),
                team=BLACK,
                expected_result=True,
            ),
        ),
    ],
)
def test_chessboard_is_expected_result(description, params):
    board = ChessBoard()
    board.load_fen_position(params["position"])
    assert board.is_expected_result(params["team"]) == params["expected_result"]


@pytest.mark.parametrize(
    "description, params",
    [
        (
            "starting position",
            dict(
                position="/".join(
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
                team=WHITE,
                expected_result=False,
            ),
        ),
        (
            "classic back rank",
            dict(
                position="/".join(
                    [
                        ".k..R...",
                        "ppp..ppp",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                    ]
                ),
                team=BLACK,
                expected_result=True,
            ),
        ),
        (
            "back rank except the king has a square",
            dict(
                position="/".join(
                    [
                        "..k.R...",
                        "ppp.....",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                    ]
                ),
                team=BLACK,
                expected_result=False,
            ),
        ),
        (
            "back rank except we can block it",
            dict(
                position="/".join(
                    [
                        "..k.R...",
                        "pppp....",
                        "........",
                        "......b.",
                        "........",
                        "........",
                        "........",
                        "........",
                    ]
                ),
                team=BLACK,
                expected_result=False,
            ),
        ),
        (
            "back rank except the king can capture",
            dict(
                position="/".join(
                    [
                        "...kR...",
                        "pppp....",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                        "........",
                    ]
                ),
                team=BLACK,
                expected_result=False,
            ),
        ),
        (
            "back rank except the piece can be captured",
            dict(
                position="/".join(
                    [
                        "k...R...",
                        "pppp....",
                        "........",
                        "........",
                        "........",
                        "....q...",
                        "........",
                        "........",
                    ]
                ),
                team=BLACK,
                expected_result=False,
            ),
        ),
        (
            "scholar's mate",
            dict(
                position="/".join(
                    [
                        "r.bqkbnr",
                        "pppp.Qpp",
                        "..n.....",
                        "....pp..",
                        "..B.P...",
                        "........",
                        "PPPP.PPP",
                        "RNB.K.NR",
                    ]
                ),
                team=BLACK,
                expected_result=True,
            ),
        ),
        (
            "the bishop can't block because it's pinned",
            dict(
                position="/".join(
                    [
                        "k.......",
                        ".b......",
                        "...B....",
                        "...Q....",
                        "........",
                        "RR......",
                        "........",
                        "........",
                    ]
                ),
                team=BLACK,
                expected_result=True,
            ),
        ),
    ],
)
def test_chessboard_is_checkmated(description, params):
    board = ChessBoard()
    board.load_fen_position(params["position"])
    assert board.is_checkmated(params["team"]) == params["expected_result"]
