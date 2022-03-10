import string
from copy import deepcopy
from typing import Dict, List, Set

from chess.constants import WHITE, BLACK, Teams, ROOK, KNIGHT, BISHOP, QUEEN, KING, PAWN
from chess.engine.classes.piece import Piece
from chess.engine.classes.position import Position
from chess.engine.classes.square import Square
from chess.engine.classes.move import Move
from chess.engine.exceptions import InvalidMove
from chess.engine.utils import get_squares

from chess.notation import (
    parse_pgn_move,
    parse_fen_string,
    parse_fen_position,
    generate_fen_position,
)
from chess.utils import other_team


class ChessBoard:
    position: Position
    move_counter: int = 0
    history: List[Position] = None
    active_team: Teams = WHITE

    def __init__(self, height=None, width=None, position=None):
        self.history = []
        self.history.append(position or Position(height=height, width=width))

    def __str__(self):
        return str(self.position)

    @property
    def position(self):
        return self.history[self.move_counter]

    def get_moves(self, current_square: Square) -> Set[Move]:
        """Given a square, find the legal moves for the piece on that square. This includes
        preventing putting self in check etc"""
        piece = self.position.get(current_square)
        if not piece:
            return set()
        squares = piece.get_squares(current_square, self.position)
        moves = set()
        for square in squares:
            captured_piece = self.position.get(square)
            move = Move(
                origin=current_square,
                destination=square,
                piece=piece,
                captured_piece=captured_piece,
                captured_piece_square=square if captured_piece else None,  # todo: en passant
            )
            moves.add(move)
        # moves = {move for move in moves if self.is_move_legal(move)}
        return moves

    def get_squares(self, square: Square) -> Set[Square]:
        """Given a square, find the legal squares for the piece on that square."""
        return {move.destination for move in self.get_moves(square)}

    def team_moves(self, team: Teams) -> Set[Move]:
        """Get all the moves for a given team. """

    def do_move(self, move: Move):
        new_position = Position({**self.position})
        new_position.do_move(move)
        self.history.append(new_position)
        self.move_counter += 1
        self.update_active_team()
        # todo: update any non-position-specific history stuff like castling rights
        # todo: overwrite any upstream moves in the history (or branch the tree?)

    def undo_move(self, move: Move):
        """reverse of above"""
        self.back()
        self.history.pop()

    def next(self):
        """Go to next move"""
        self.move_counter += 1

    def back(self):
        """Go to prev move"""
        self.move_counter -= 1

    def is_checkmated(self, team: Teams) -> bool:
        """Is the team checkmated"""

    def is_in_check(self, team: Teams) -> bool:
        """Is the team checkmated"""

    def load_standard_setup(self):
        self.history = []
        self.move_counter = 0
        position = Position()
        position.add(Piece(WHITE, ROOK), Square(0, 0))
        position.add(Piece(WHITE, KNIGHT), Square(1, 0))
        position.add(Piece(WHITE, BISHOP), Square(2, 0))
        position.add(Piece(WHITE, QUEEN), Square(3, 0))
        position.add(Piece(WHITE, KING), Square(4, 0))
        position.add(Piece(WHITE, BISHOP), Square(5, 0))
        position.add(Piece(WHITE, KNIGHT), Square(6, 0))
        position.add(Piece(WHITE, ROOK), Square(7, 0))
        position.add(Piece(BLACK, ROOK), Square(0, 7))
        position.add(Piece(BLACK, KNIGHT), Square(1, 7))
        position.add(Piece(BLACK, BISHOP), Square(2, 7))
        position.add(Piece(BLACK, QUEEN), Square(3, 7))
        position.add(Piece(BLACK, KING), Square(4, 7))
        position.add(Piece(BLACK, BISHOP), Square(5, 7))
        position.add(Piece(BLACK, KNIGHT), Square(6, 7))
        position.add(Piece(BLACK, ROOK), Square(7, 7))
        for x in range(8):
            position.add(Piece(WHITE, PAWN), Square(x, 1))
            position.add(Piece(BLACK, PAWN), Square(x, 6))
        self.history.append(position)

    def load_fen_position(self, string):
        # todo: read current player from FEN
        position = Position.from_fen(string)
        self.history = []
        self.history.append(position)
        self.move_counter = 0
        self.active_team = WHITE

    @property
    def fen_position(self) -> str:
        return generate_fen_position(self.position)

    def do_pgn_move(self, string):
        # parse PGN notation and create Move class
        piece_type, specifier, capture, square_name = parse_pgn_move(string)
        target_square = Square.from_str(square_name)
        candidate_pieces = [
            (square, piece)
            for square, piece in self.position.items()
            if piece.type == piece_type
            and piece.team == self.active_team
            and target_square in get_squares(square, self.position)
        ]
        if specifier:
            if specifier.isnumeric():
                y = Square.number_to_y(specifier)
                candidate_pieces = [
                    (square, piece) for square, piece in candidate_pieces if square.y == y
                ]
            else:
                x = Square.letter_to_x(specifier)
                candidate_pieces = [
                    (square, piece) for square, piece in candidate_pieces if square.x == x
                ]

        try:
            square, piece = candidate_pieces[0]
        except IndexError:
            raise InvalidMove(f"No {piece_type} can reach {target_square.to_str()}")
        captured_piece = self.position.get(target_square)  # not true for en passant
        move = Move(
            origin=square,
            destination=target_square,
            piece=piece,
            captured_piece=captured_piece,
            captured_piece_square=target_square if captured_piece else None,
        )
        # check legality?
        self.do_move(move)

    def update_active_team(self):
        self.active_team = other_team(self.active_team)


# class ChessBoard:
#     contents: Dict[Square, Piece]
#     height: int = 8
#     width: int = 8
#     current_player: str = WHITE
#
#     def __init__(self, height=None, width=None):
#         self.contents = dict()
#         self.height = height if height else self.height
#         self.width = width if width else self.width
#         self.squares = tuple(Square(x, y) for y in range(self.height) for x in range(self.width))
#
#     def get(self, *args, **kwargs) -> Piece:
#         return self.contents.get(*args, **kwargs)
#
#     def load_fen_position(self, string):
#         # todo: read current player from FEN
#         position, *_ = parse_fen_string(string)
#         pieces = parse_fen_position(position)
#         # using add_piece here makes sure the piece gets a ref to board.
#         for square, piece in pieces.items():
#             self.add_piece(piece, square)
#
#     @property
#     def fen_position(self) -> str:
#         return generate_fen_position(self.contents)
#
#     def do_pgn_move(self, string):
#         piece_class, specifier, capture, square_name = parse_pgn_move(string)
#         target_square = self.square_coords(square_name)
#         candidate_pieces = [
#             piece
#             for coords, piece in self.contents.items()
#             if isinstance(piece, piece_class)
#             and target_square in piece.squares
#             and piece.team == self.current_player
#         ]
#         if specifier:
#             if specifier.isnumeric():
#                 y = self.number_to_y(specifier)
#                 candidate_pieces = [piece for piece in candidate_pieces if piece.square.y == y]
#             else:
#                 x = self.letter_to_x(specifier)
#                 candidate_pieces = [piece for piece in candidate_pieces if piece.square.x == x]
#
#         piece = candidate_pieces[0]
#         move = Move(piece.square, target_square)
#         self.do_move(move)
#
#     def add_piece(self, piece: Piece, square: Square):
#         square = Square(*square)
#         self.contents[square] = piece
#         piece.board = self
#
#     def remove_piece(self, square: Square):
#         del self.contents[square]
#
#     def do_move(self, move: Move):
#         square1, square2 = move
#         self.contents[square2] = self.contents.pop(square1)
#
#     def locate(self, piece: Piece) -> Square:
#         """Get coordinates of Piece instance"""
#         for coords, p in self.contents.items():
#             if p is piece:
#                 return Square(*coords)
#
#     def get_king(self, team: str) -> King:
#         return next(p for p in self.contents.values() if isinstance(p, King) and p.team == team)
#
#     def is_in_check(self, team: str) -> bool:
#         threatened_squares = []
#         for coords, piece in self.contents.items():
#             if piece.team == team:
#                 continue  # can't be in check from our own pieces
#             threatened_squares.extend(piece.captures if isinstance(piece, Pawn) else piece.squares)
#         king = self.get_king(team)
#         return king.square in threatened_squares
#
#     def is_checkmated(self, team: str) -> bool:
#         # is it check
#         if not self.is_in_check(team):
#             return False
#
#         # can any move make it not check
#         for move in self.team_moves(team):
#             new_position = self.after_move(move)
#             if not new_position.is_in_check(team):
#                 return False
#
#         return True
#
#     def is_stalemated(self, team: str) -> bool:
#         return not self.team_legal_moves(team) and not self.is_in_check(team)
#
#     def is_move_legal(self, move: Move) -> bool:
#         square1, square2 = move
#         piece = self.contents.get(square1)
#         team = piece.team
#         new_position = self.after_move(move)
#         return square2 in piece.squares and not new_position.is_in_check(team)
#
#     def team_moves(self, team: str) -> List[Move]:
#         return [
#             Move(piece.square, square)
#             for coords, piece in self.contents.items()
#             for square in piece.squares
#             if piece.team == team
#         ]
#
#     def team_legal_moves(self, team: str) -> List[Move]:
#         return [move for move in self.team_moves(team) if self.is_move_legal(move)]
#
#     def piece_legal_moves(self, piece_square: Square) -> List[Move]:
#         piece = self.contents.get(piece_square)
#         return [
#             Move(piece_square, square2)
#             for square2 in piece.squares
#             if self.is_move_legal(Move(piece_square, square2))
#         ]
