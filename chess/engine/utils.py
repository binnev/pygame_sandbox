from typing import TYPE_CHECKING

from chess.constants import Teams, KING

if TYPE_CHECKING:
    from chess.engine.classes.position import Position


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
