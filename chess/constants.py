from enum import Enum

PAWN = "pawn"
KING = "king"
QUEEN = "queen"
BISHOP = "bishop"
KNIGHT = "knight"
ROOK = "rook"


class PieceTypes(Enum):
    PAWN = PAWN
    KING = KING
    QUEEN = QUEEN
    BISHOP = BISHOP
    KNIGHT = KNIGHT
    ROOK = ROOK


WHITE = "white"
BLACK = "black"
RED = "red"
BLUE = "blue"


class Teams(Enum):
    WHITE = WHITE
    BLACK = BLACK
    RED = RED
    BLUE = BLUE


PIECE_TO_LETTER = {
    KING: "k",
    QUEEN: "q",
    BISHOP: "b",
    KNIGHT: "n",
    ROOK: "r",
    PAWN: "p",
}

LETTER_TO_PIECE = {v: k for k, v in PIECE_TO_LETTER.items()}

PIECE_TO_SYMBOL = {
    BLACK: {
        KING: "♔",
        QUEEN: "♕",
        BISHOP: "♗",
        KNIGHT: "♘",
        ROOK: "♖",
        PAWN: "♙",
    },
    WHITE: {
        KING: "♚",
        QUEEN: "♛",
        BISHOP: "♝",
        KNIGHT: "♞",
        ROOK: "♜",
        PAWN: "♟",
    },
}


BISHOP_DIRECTIONS = ((1, 1), (1, -1), (-1, 1), (-1, -1))
ROOK_DIRECTIONS = ((0, 1), (0, -1), (1, 0), (-1, 0))
KNIGHT_DIRECTIONS = ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2))
