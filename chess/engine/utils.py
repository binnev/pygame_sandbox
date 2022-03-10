from math import inf
from typing import Set, TYPE_CHECKING

from numpy import array

from chess.constants import (
    WHITE,
    PieceTypes,
    Teams,
    PAWN,
    KING,
    QUEEN,
    BISHOP,
    KNIGHT,
    ROOK,
    BISHOP_DIRECTIONS,
    ROOK_DIRECTIONS,
    KNIGHT_DIRECTIONS,
)
from chess.engine.classes.square import Square

if TYPE_CHECKING:
    from chess.engine.classes.position import Position
    from chess.engine.classes.piece import Piece


def is_in_check(team: Teams, position: "Position") -> bool:
    """
    locate king of the team
    get opposing team's squares
    check if king is in squares
    """
    king_square = next(s for s, p in position.items() if p.type == KING and p.team == team)
    opponent_pieces = {s: p for s, p in position.items() if p.team != team}
    opponent_squares = set()
    for square, piece in opponent_pieces.items():
        opponent_squares = opponent_squares.union(piece.get_squares(square, position))
    return king_square in opponent_squares


def is_checkmated(team: Teams, position: "Position") -> bool:
    # is it check
    if not is_in_check(team, position):
        return False

    # can any move make it not check
    team_pieces = {s: p for s, p in position.items() if p.team == team}
    for square, piece in team_pieces.items():
        for move in piece.get_moves(...):
            position.do_move(move)
            is_check = is_in_check(team, position)
            position.undo_move(move)
            if not is_check:
                return False

    return True


def is_stalemated(self, team: str) -> bool:
    return not self.team_legal_moves(team) and not self.is_in_check(team)


def get_squares(current_square: Square, position: "Position", piece: "Piece") -> Set[Square]:
    """Find the squares that this piece could possibly move to from the current_square,
    ignoring special rules:
    - en passant
    - castling
    - putting self in check
    """

    if piece.type == PAWN:
        return get_pawn_squares(current_square=current_square, position=position, team=piece.team)

    squares = set()
    directions = {
        BISHOP: BISHOP_DIRECTIONS,
        ROOK: ROOK_DIRECTIONS,
        KNIGHT: KNIGHT_DIRECTIONS,
        KING: ROOK_DIRECTIONS + BISHOP_DIRECTIONS,
        QUEEN: ROOK_DIRECTIONS + BISHOP_DIRECTIONS,
    }[piece.type]
    strides = {BISHOP: inf, ROOK: inf, KNIGHT: 1, KING: 1, QUEEN: inf}[piece.type]
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
            or position.get(square).team != piece.team  # only capture enemies
        )
    }


def get_pawn_captures(current_square: Square, position: "Position", team: Teams) -> Set[Square]:
    capture_directions = [(1, 1), (-1, 1)] if team == WHITE else [(1, -1), (-1, -1)]
    capture_directions = [array(d) for d in capture_directions]
    capture_squares = [tuple(d + current_square) for d in capture_directions]
    moves = {s for s in capture_squares if position.get(s) and position.get(s).team != team}
    return {move for move in moves if move in position.squares}


def get_pawn_squares(current_square: Square, position: "Position", team: Teams) -> Set[Square]:
    move_direction = array((0, 1) if team == WHITE else (0, -1))
    move_square1 = Square(*tuple(move_direction + current_square))
    move_square2 = Square(*tuple(move_direction * 2 + current_square))
    moves = get_pawn_captures(current_square=current_square, position=position, team=team)
    if not position.get(move_square1):
        moves.add(move_square1)
        if position.is_pawn_starting_square(current_square, team) and not position.get(
            move_square2
        ):
            moves.add(move_square2)
    return {move for move in moves if move in position.squares}
