import re
from typing import Type, TYPE_CHECKING, List, Union, Dict

from chess.constants import WHITE, BLACK
from chess.engine.classes.piece import Piece, Pawn, CLASSES_BY_LETTER

if TYPE_CHECKING:
    from chess.engine.classes.board import ChessBoard


def parse_pgn_move(string: str) -> (Type[Piece], str, str, str):
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


def parse_fen_row(string: str) -> List[Union[Piece, None]]:
    """
    E.g. pppp1ppp
    """
    pieces = []
    for char in string:
        if char.isnumeric():
            pieces.extend([None] * int(char))
        elif char.isalpha():
            piece_class = CLASSES_BY_LETTER[char.lower()]
            team = WHITE if char.isupper() else BLACK
            pieces.append(piece_class(team))
        else:
            # if it is a filler character e.g. "."
            pieces.append(None)
    return pieces


def parse_fen_string(string: str) -> (str, str, str, str, str, str):
    """
    E.g. standard starting position:
    rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
    """
    rx = re.compile(
        "([\w./]+)"  # piece positions from white's POV
        " ([wb])?"  # active player (w = white | b = black)
        " (K?Q?k?q?)?"  # castling availability (K = white kingside, q = black queenside)
        " ([\S])?"  # en passant target square (- = standard)
        " (\d+)?"  # Halfmove clock: The number of halfmoves since the last capture or pawn
        # advance, used for the fifty-move rule.
        " (\d+)?"  # Fullmove number: The number of the full move. It starts at 1,
        # and is incremented after Black's move
    )
    position, player, castling, ep, half, full = rx.match(string).groups()
    return position, player, castling, ep, half, full


def parse_fen_position(string: str) -> Dict[tuple, Piece]:
    """
    E.g. standard starting position:
    rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR
    """
    pieces = dict()
    rows = string.split("/")
    for y, row in enumerate(rows):
        y = 7 - y
        row = parse_fen_row(row)
        for x, piece in enumerate(row):
            if piece:
                pieces[(x, y)] = piece

    return pieces


def generate_fen_row(row: List[Union[Piece, None]]) -> str:
    string = ""
    empty_squares = 0
    for square in row:
        if isinstance(square, Piece):
            string += str(empty_squares) if empty_squares else ""
            string += str(square)
            empty_squares = 0
        else:
            empty_squares += 1

    string += str(empty_squares) if empty_squares else ""
    return string


def generate_fen_position(pieces: Dict[tuple, Piece]) -> str:
    xs = range(8)
    ys = range(0, -8, -1)
    rows = []
    for y in range(min(ys), max(ys) + 1):
        row = [pieces.get((x, -y)) for x in range(min(xs), max(xs) + 1)]
        rows.append(generate_fen_row(row))
    return "/".join(rows)
