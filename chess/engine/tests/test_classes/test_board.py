from chess.engine.classes import ChessBoard, King, WHITE, BLACK


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
