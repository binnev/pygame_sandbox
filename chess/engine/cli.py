from chess.engine.classes.board import ChessBoard

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
        except Exception:
            print(f"invalid move: {move}")
        else:
            board.switch_player()
