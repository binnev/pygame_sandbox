from chess.constants import Teams
from chess.engine.classes.move import Move
from chess.notation import parse_fen_string, parse_fen_position


class FenPosition(str):
    """
    Based on FEN string, e.g. "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR = position
    w | b = active player
    KQkq = casting availability (K = white kingside, q = black queenside)
    - = en passant target square (- is standard)
    0 = Halfmove clock: The number of halfmoves since the last capture or pawn advance,
        used for the fifty-move rule
    1 = Fullmove number: The number of the full move. It starts at 1, and is incremented
        after Black's move
    """

    def __init__(self, string):
        (
            position,
            active_player,
            castling_rights,
            ep,
            halfmove_clock,
            fullmove_clock,
        ) = parse_fen_string(string)
        pieces = parse_fen_position(position)
        self.pieces = tuple(pieces.items())
        self.active_player = active_player == "w"
        self.white_can_castle_kingside = "K" in castling_rights
        self.white_can_castle_queenside = "Q" in castling_rights
        self.black_can_castle_kingside = "k" in castling_rights
        self.black_can_castle_queenside = "q" in castling_rights
        self.halfmove_clock = int(halfmove_clock)
        self.fullmove_clock = int(fullmove_clock)
        self.available_moves = ...  # pgn moves? or Move class?
        self.is_check = is_in_check(self)
        # self.is_game_over, self.winner = None, None # todo

    def do_move(self, move: Move):
        pass

    def to_string(self) -> str:
        position = self.split(" ")[0]

    @classmethod
    def initial(cls):
        return cls("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")


def is_in_check(position: FenPosition) -> bool:
    pass


def available_moves(position: FenPosition) -> list[Move]:
    pass
