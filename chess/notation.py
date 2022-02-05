from chess.engine.classes import WHITE, BLACK, Pawn, Rook, Knight, Bishop, Queen, King
import re

EMPTY = "."


def parse_pgn_move(string):
    """ for string = "Rbxa4" """
    rx = re.compile(
        "([A-Z])?"  # piece
        "([a-wy-z0-9])?"  # additional specifier (not x)
        "(x)?"  # capture specifier
        "([a-z][0-9])"  # target square
    )

    piece, specifier, capture, target = rx.match(string).groups()
    if piece is None:
        piece = "P"  # pawn by default
    return piece, specifier, capture, target


def parse_fen_row(string):
    """
    E.g. pppp1ppp
    """
    pieces = []

    # todo move to pieces module
    piece_mapping = dict(
        p=Pawn,
        r=Rook,
        n=Knight,
        b=Bishop,
        q=Queen,
        k=King,
    )
    for char in string:
        if char.isnumeric():
            pieces.extend([EMPTY] * int(char))
        else:
            piece_class = piece_mapping[char.lower()]
            team = WHITE if char.isupper() else BLACK
            pieces.append(piece_class(team))

    return pieces


# def parse_fen_position(string):
#     """
#     E.g. standard starting position:
#     rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
#     """
#     rx = re.compile(
#         "(\w+/\w+/\w+/\w+/\w+/\w+/\w+/\w+)"  # piece positions from white's POV
#         " ([wb])?"  # active player (w = white | b = black)
#         # " (K?Q?k?q?)?"  # castling availability (K = white kingside, q = black queenside)
#         # " ([\S])?"  # en passant target square (- = standard)
#         # " (\d+)?"  # Halfmove clock: The number of halfmoves since the last capture or pawn
#         # # advance, used for the fifty-move rule.
#         # " (\d+)?"  # Fullmove number: The number of the full move. It starts at 1,
#         # # and is incremented after Black's move
#     )
#     position, *_ = rx.match(string).groups()
#
#     rows = position.split("/")
#     for ii, row in enumerate(rows):
#         parse_fen_row(row, ii)
#
#     return position, _
