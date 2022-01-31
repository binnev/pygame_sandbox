import re


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
