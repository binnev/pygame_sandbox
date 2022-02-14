import string
from collections import namedtuple
from copy import deepcopy
from typing import Dict, Tuple, List

from chess.constants import WHITE, BLACK
from chess.engine.classes.piece import Piece, Rook, Knight, Bishop, Queen, King, Pawn
from chess.engine.typing import Square, Move
from chess.notation import (
    parse_pgn_move,
    parse_fen_string,
    parse_fen_position,
    generate_fen_position,
)


class ChessBoard:
    contents: Dict[Square, Piece]
    height: int = 8
    width: int = 8
    current_player: str = WHITE

    def __init__(self, height=None, width=None):
        self.contents = dict()
        self.height = height if height else self.height
        self.width = width if width else self.width
        self.squares = tuple(Square(x, y) for y in range(self.height) for x in range(self.width))

    def get(self, *args, **kwargs) -> Piece:
        return self.contents.get(*args, **kwargs)

    def load_standard_setup(self):
        self.add_piece(Rook(WHITE), (0, 0))
        self.add_piece(Knight(WHITE), (1, 0))
        self.add_piece(Bishop(WHITE), (2, 0))
        self.add_piece(Queen(WHITE), (3, 0))
        self.add_piece(King(WHITE), (4, 0))
        self.add_piece(Bishop(WHITE), (5, 0))
        self.add_piece(Knight(WHITE), (6, 0))
        self.add_piece(Rook(WHITE), (7, 0))
        self.add_piece(Rook(BLACK), (0, 7))
        self.add_piece(Knight(BLACK), (1, 7))
        self.add_piece(Bishop(BLACK), (2, 7))
        self.add_piece(Queen(BLACK), (3, 7))
        self.add_piece(King(BLACK), (4, 7))
        self.add_piece(Bishop(BLACK), (5, 7))
        self.add_piece(Knight(BLACK), (6, 7))
        self.add_piece(Rook(BLACK), (7, 7))
        for x in range(8):
            self.add_piece(Pawn(WHITE), (x, 1))
            self.add_piece(Pawn(BLACK), (x, 6))

    def load_fen_position(self, string):
        # todo: read current player from FEN
        position, *_ = parse_fen_string(string)
        pieces = parse_fen_position(position)
        # using add_piece here makes sure the piece gets a ref to board.
        for square, piece in pieces.items():
            self.add_piece(piece, square)

    @property
    def fen_position(self) -> str:
        return generate_fen_position(self.contents)

    def do_pgn_move(self, string):
        piece_class, specifier, capture, square_name = parse_pgn_move(string)
        target_square = self.square_coords(square_name)
        candidate_pieces = [
            piece
            for coords, piece in self.contents.items()
            if isinstance(piece, piece_class)
            and target_square in piece.moves
            and piece.team == self.current_player
        ]
        if specifier:
            if specifier.isnumeric():
                y = self.number_to_y(specifier)
                candidate_pieces = [piece for piece in candidate_pieces if piece.square.y == y]
            else:
                x = self.letter_to_x(specifier)
                candidate_pieces = [piece for piece in candidate_pieces if piece.square.x == x]

        piece = candidate_pieces[0]
        move = Move(piece.square, target_square)
        self.do_move(move)

    def add_piece(self, piece: Piece, square: Square):
        square = Square(*square)
        self.contents[square] = piece
        piece.board = self

    def remove_piece(self, square: Square):
        del self.contents[square]

    def do_move(self, move: Move):
        square1, square2 = move
        self.contents[square2] = self.contents.pop(square1)

    def __str__(self, V_SEP="\n", H_SEP=" ") -> str:
        xs = range(self.width)
        ys = range(0, -self.height, -1)
        return V_SEP.join(
            H_SEP.join(str(self.contents.get((x, -y), ".")) for x in range(min(xs), max(xs) + 1))
            for y in range(min(ys), max(ys) + 1)
        )

    @classmethod
    def number_to_y(cls, number: str) -> int:
        return int(number) - 1

    @classmethod
    def letter_to_x(cls, letter: str) -> int:
        return string.ascii_lowercase.index(letter)

    @classmethod
    def square_coords(cls, name: str) -> Square:
        """
        a1 -> (0, 0)
        h8 -> (7, 7)
        """
        letter, number = name.lower()
        return Square(x=cls.letter_to_x(letter), y=cls.number_to_y(number))

    @classmethod
    def y_to_number(cls, y: int) -> str:
        return str(y + 1)

    @classmethod
    def x_to_letter(cls, x: int) -> str:
        return string.ascii_lowercase[x]

    @classmethod
    def square_name(cls, square: Square) -> str:
        """
        (0, 0) -> a1
        (7, 7) -> h8
        """
        x, y = square
        number = cls.y_to_number(y)
        letter = cls.x_to_letter(x)
        return letter + number

    def locate(self, piece: Piece) -> Square:
        """Get coordinates of Piece instance"""
        for coords, p in self.contents.items():
            if p is piece:
                return Square(*coords)

    def pawn_starting_squares(self, team) -> List[Square]:
        return (
            [Square(x, 1) for x in range(self.width)]
            if team == WHITE
            else [Square(x, self.height - 2) for x in range(self.width)]
        )

    def is_pawn_on_starting_square(self, pawn: Pawn) -> bool:
        return pawn.square in self.pawn_starting_squares(pawn.team)

    def switch_player(self):
        self.current_player = WHITE if self.current_player == BLACK else BLACK

    def get_king(self, team: str) -> King:
        return next(p for p in self.contents.values() if isinstance(p, King) and p.team == team)

    def is_in_check(self, team: str) -> bool:
        threatened_squares = []
        for coords, piece in self.contents.items():
            if piece.team == team:
                continue  # can't be in check from our own pieces
            threatened_squares.extend(piece.captures if isinstance(piece, Pawn) else piece.moves)
        king = self.get_king(team)
        return king.square in threatened_squares

    def after_move(self, move: Move) -> "ChessBoard":
        new_position = deepcopy(self)
        new_position.do_move(move)
        return new_position

    def is_checkmated(self, team: str) -> bool:
        # is it check
        if not self.is_in_check(team):
            return False

        # can any move make it not check
        for move in self.team_moves(team):
            new_position = self.after_move(move)
            if not new_position.is_in_check(team):
                return False

        return True

    def is_stalemated(self, team: str) -> bool:
        return not self.team_legal_moves(team) and not self.is_in_check(team)

    def is_move_legal(self, move: Move) -> bool:
        square1, square2 = move
        moving_piece = self.contents.get(square1)
        team = moving_piece.team
        new_position = self.after_move(move)
        return square2 in self.squares and not new_position.is_in_check(team)

    def team_moves(self, team: str) -> List[Move]:
        return [
            Move(piece.square, square)
            for coords, piece in self.contents.items()
            for square in piece.moves
            if piece.team == team
        ]

    def team_legal_moves(self, team: str) -> List[Move]:
        return [move for move in self.team_moves(team) if self.is_move_legal(move)]

    def piece_legal_moves(self, piece_square: Square) -> List[Move]:
        piece = self.contents.get(piece_square)
        return [
            Move(piece_square, square2)
            for square2 in piece.moves
            if self.is_move_legal(Move(piece_square, square2))
        ]
