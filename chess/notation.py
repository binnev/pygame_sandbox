import re
from typing import Type

from chess.constants import WHITE, BLACK
from chess.engine.classes.piece import Piece, Pawn, CLASSES_BY_LETTER


def parse_pgn_move(string) -> (Type[Piece], str, str, str):
    """ e.g. "Rbxa4" """
    rx = re.compile(
        "([A-Z])?"  # piece
        "([a-wy-z0-9])?"  # additional specifier (not x)
        "(x)?"  # capture specifier
        "([a-z][0-9])"  # target square
    )

    letter, specifier, capture, target = rx.match(string).groups()
    piece_class = CLASSES_BY_LETTER[letter.lower()] if letter else Pawn
    return piece_class, specifier, capture, target


def parse_fen_row(string):
    """
    E.g. pppp1ppp
    """
    pieces = []
    for char in string:
        if char.isnumeric():
            pieces.extend([None] * int(char))
        else:
            piece_class = CLASSES_BY_LETTER[char.lower()]
            team = WHITE if char.isupper() else BLACK
            pieces.append(piece_class(team))
    return pieces


def parse_fen_position(string):
    """
    E.g. standard starting position:
    rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
    """
    rx = re.compile(
        "(\w+/\w+/\w+/\w+/\w+/\w+/\w+/\w+)"  # piece positions from white's POV
        " ([wb])?"  # active player (w = white | b = black)
        # " (K?Q?k?q?)?"  # castling availability (K = white kingside, q = black queenside)
        # " ([\S])?"  # en passant target square (- = standard)
        # " (\d+)?"  # Halfmove clock: The number of halfmoves since the last capture or pawn
        # # advance, used for the fifty-move rule.
        # " (\d+)?"  # Fullmove number: The number of the full move. It starts at 1,
        # # and is incremented after Black's move
    )
    position, *_ = rx.match(string).groups()

    pieces = dict()
    rows = position.split("/")
    for y, row in enumerate(rows):
        y = 7 - y
        row = parse_fen_row(row)
        for x, piece in enumerate(row):
            if piece:
                pieces[(x, y)] = piece

    return pieces, _
