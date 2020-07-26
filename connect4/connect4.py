import numpy as np

ROW_COUNT = 8
COLUMN_COUNT = 12


def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)
    return board


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def print_board(board):
    print(np.flip(board, 0))


def winning_move(board, piece):
    # Check horizontal locations for the win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if (
                board[r][c] == piece
                and board[r][c + 1] == piece
                and board[r][c + 2] == piece
                and board[r][c + 3] == piece
            ):
                return True


def get_diagonals(board):
    def _get_diagonals(board):
        height, width = board.shape
        return [list(np.diag(board, k=k)) for k in range(-height + 1, width)]

    return _get_diagonals(board) + _get_diagonals(np.rot90(board))


def slice_winner(input):
    input = list(input)
    for player in (1, 2):
        if input.count(player) < 4:
            continue
        # find first occurrence of player piece
        index = input.index(player)
        pieces_in_a_row = 0
        for ii in range(4):
            if input[index + ii] == player:
                pieces_in_a_row += 1

        if pieces_in_a_row >= 4:
            return player


def winner(board):
    slices = [row for row in board] + [col for col in board.T] + get_diagonals(board)
    for s in slices:
        win = slice_winner(s)
        if win:
            return win


def main():
    board = create_board()
    game_over = False
    turn = 0

    print_board(board)
    while not game_over:
        player = 1 if turn == 0 else 2
        col = int(input(f"Player {player}, make your selection (0-6):"))
        print(f"Player {player} selected column {col}")

        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, player)
            print_board(board)

            if winner(board) == player:
                print(f"PLAYER {player} WINS!!! CONGRATULATIONS!")
                game_over = True

        turn += 1
        turn = turn % 2


if __name__ == "__main__":
    main()
