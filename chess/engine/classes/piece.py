from math import inf
from typing import Set, NamedTuple, TYPE_CHECKING

from numpy import array

from chess.constants import (
    WHITE,
    BLACK,
    PieceTypes,
    Teams,
    LETTER_TO_PIECE,
    PIECE_TO_SYMBOL,
    PAWN,
    KING,
    QUEEN,
    BISHOP,
    KNIGHT,
    ROOK,
)
from chess.engine.classes.square import Square

if TYPE_CHECKING:
    from chess.engine.classes.position import Position

BISHOP_DIRECTIONS = ((1, 1), (1, -1), (-1, 1), (-1, -1))
ROOK_DIRECTIONS = ((0, 1), (0, -1), (1, 0), (-1, 0))
KNIGHT_DIRECTIONS = ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2))


class Piece(NamedTuple):
    """Knows its type and team. Does not know its location (square)"""

    team: Teams
    type: PieceTypes

    def __str__(self):
        return PIECE_TO_SYMBOL[self.team][self.type]

    @classmethod
    def from_letter(cls, letter: str):
        """Note: limited to traditional black/white only"""
        team = WHITE if letter.isupper() else BLACK
        letter = letter.lower()
        piece_type = LETTER_TO_PIECE[letter]
        return cls(team, piece_type)

    def get_squares(self, current_square: Square, position: "Position") -> Set[Square]:
        """
        Select move generator function based on piece type
        generate moves
        return moves
        """
        return get_squares(
            current_square=current_square, position=position, team=self.team, piece_type=self.type
        )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.team} {self.type})"


def get_squares(
    current_square: Square, position: "Position", piece_type: PieceTypes, team: Teams
) -> Set[Square]:
    if piece_type == PAWN:
        return get_pawn_squares(current_square=current_square, position=position, team=team)

    squares = set()
    directions = {
        BISHOP: BISHOP_DIRECTIONS,
        ROOK: ROOK_DIRECTIONS,
        KNIGHT: KNIGHT_DIRECTIONS,
        KING: ROOK_DIRECTIONS + BISHOP_DIRECTIONS,
        QUEEN: ROOK_DIRECTIONS + BISHOP_DIRECTIONS,
    }[piece_type]
    strides = {BISHOP: inf, ROOK: inf, KNIGHT: 1, KING: 1, QUEEN: inf}[piece_type]
    for direction in directions:
        direction = array(direction)
        candidate = current_square
        ii = 0
        while candidate in position.squares and ii < strides:
            candidate = Square(*tuple(direction + candidate))
            squares.add(candidate)
            if position.get(candidate):
                break
            ii += 1

    return {
        square
        for square in squares
        if square in position.squares
        and (
            position.get(square) is None  # empty squares
            or position.get(square).team != team  # only capture enemies
        )
    }


def pawn_captures(current_square: Square, position: "Position", team: Teams) -> Set[Square]:
    capture_directions = [(1, 1), (-1, 1)] if team == WHITE else [(1, -1), (-1, -1)]
    capture_directions = [array(d) for d in capture_directions]
    capture_squares = [tuple(d + current_square) for d in capture_directions]
    moves = {s for s in capture_squares if position.get(s) and position.get(s).team != team}
    return {move for move in moves if move in position.squares}


def get_pawn_squares(current_square: Square, position: "Position", team: Teams) -> Set[Square]:
    move_direction = array((0, 1) if team == WHITE else (0, -1))
    move_square1 = Square(*tuple(move_direction + current_square))
    move_square2 = Square(*tuple(move_direction * 2 + current_square))
    moves = pawn_captures(current_square=current_square, position=position, team=team)
    if not position.get(move_square1):
        moves.add(move_square1)
        if position.is_pawn_starting_square(current_square, team) and not position.get(
            move_square2
        ):
            moves.add(move_square2)
    return {move for move in moves if move in position.squares}


# class Piece:
#     team: str  # "white" or "black"
#     letter: str  # "k" for king
#     board: "ChessBoard"
#     square: Tuple[int, int]
#     directions: tuple  # what directions can this piece move
#     strides: int  # how many squares can this piece move along its directions
#
#     def __init__(self, team=WHITE):
#         self.team = team
#
#     def __str__(self):
#         return self.letter.upper() if self.team == WHITE else self.letter.lower()
#
#     def __repr__(self):
#         string = f"{self.team} {self.__class__.__name__}"
#         square = self.square
#         if square:
#             square = self.board.square_name(square)
#             string += f" on {square}"
#         return string
#
#     def __eq__(self, other: "Piece"):
#         return self.__class__ == other.__class__ and self.team == other.team
#
#     @property
#     def squares(self) -> Set[Square]:
#         """Set of squares this piece could move to, taking into account obstructions and board
#         edges"""
#         moves = set()
#         for direction in self.directions:
#             direction = array(direction)
#             candidate = self.square
#             ii = 0
#             while candidate in self.board.squares and ii < self.strides:
#                 candidate = tuple(direction + candidate)
#                 moves.add(candidate)
#                 if self.board.contents.get(candidate):
#                     break
#                 ii += 1
#
#         return {
#             move
#             for move in moves
#             if move in self.board.squares
#             and (
#                 self.board.contents.get(move) is None  # empty squares
#                 or self.board.contents.get(move).team != self.team  # only capture enemies
#             )
#         }
#
#     @property
#     def square(self) -> Square:
#         """Coordinates of self on board"""
#         try:
#             return self.board.locate(self)
#         except AttributeError:
#             return None
#
#     @classmethod
#     def from_letter(cls, letter: str, *args, **kwargs):
#         klass = CLASSES_BY_LETTER[letter.lower()]
#         team = WHITE if letter.isupper() else BLACK
#         return klass(*args, team=team, **kwargs)
#
#
# class King(Piece):
#     letter = "k"
#     directions = ROOK_DIRECTIONS + BISHOP_DIRECTIONS
#     strides = 1
#
#
# class Queen(Piece):
#     letter = "q"
#     directions = ROOK_DIRECTIONS + BISHOP_DIRECTIONS
#     strides = inf
#
#
# class Bishop(Piece):
#     letter = "b"
#     directions = BISHOP_DIRECTIONS
#     strides = inf
#
#
# class Knight(Piece):
#     letter = "n"
#     directions = KNIGHT_DIRECTIONS
#     strides = 1
#
#
# class Rook(Piece):
#     letter = "r"
#     directions = ROOK_DIRECTIONS
#     strides = inf
#
#
# class Pawn(Piece):
#     """
#     directions depends on team (white | black)
#     strides depends on whether it's on its starting spot
#     """
#
#     letter = "p"
#
#     @property
#     def squares(self) -> Set[Square]:
#         move_direction = array((0, 1) if self.team == WHITE else (0, -1))
#         move_square1 = tuple(move_direction + self.square)
#         move_square2 = tuple(move_direction * 2 + self.square)
#         moves = self.captures
#         if not self.board.get(move_square1):
#             moves.add(move_square1)
#             if not self.board.get(move_square2) and self.board.is_pawn_on_starting_square(self):
#                 moves.add(move_square2)
#         return {move for move in moves if move in self.board.squares}
#
#     @property
#     def captures(self):
#         capture_directions = [(1, 1), (-1, 1)] if self.team == WHITE else [(1, -1), (-1, -1)]
#         capture_directions = [array(d) for d in capture_directions]
#         capture_squares = [tuple(d + self.square) for d in capture_directions]
#         moves = {
#             s for s in capture_squares if self.board.get(s) and self.board.get(s).team != self.team
#         }
#         return {move for move in moves if move in self.board.squares}
#
