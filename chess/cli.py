from chess.constants import WHITE, BLACK
from chess.engine.classes.board import ChessBoard
from chess.engine.exceptions import IllegalMove
from chess.engine.utils import is_checkmated

if __name__ == "__main__":
    running = True
    board = ChessBoard()
    board.load_standard_setup()
    while running:
        print(board)
        if is_checkmated(WHITE, board.position):
            print("Checkmate! Black wins.")
            break
        if is_checkmated(BLACK, board.position):
            print("Checkmate! White wins.")
            break

        move = input(f"{board.active_team} to move: ").strip()
        if move in ["exit", "quit"]:
            break
        if move in ["back", "prev"]:
            board.back()
            continue
        try:
            board.do_pgn_move(move)
        except IllegalMove as e:
            print(f"invalid move: {move}; {e}")
