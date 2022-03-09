from chess.engine.classes.board import ChessBoard
from chess.engine.exceptions import InvalidMove

if __name__ == "__main__":
    running = True
    board = ChessBoard()
    board.load_standard_setup()
    while running:
        print(board)
        move = input("enter move: ")
        if move.strip() in ["exit", "quit"]:
            break
        try:
            board.do_pgn_move(move)
        except InvalidMove as e:
            print(f"invalid move: {move}; {e}")
