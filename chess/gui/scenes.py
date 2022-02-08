from typing import TYPE_CHECKING

from base.objects import Entity, Group
from chess.gui.classes.piece import Pawn, King, Queen, Rook, Knight, Bishop

if TYPE_CHECKING:
    from chess.gui.game import ChessGame


class ChessMatch(Entity):

    game: "ChessGame"

    def __init__(self, *groups):
        super().__init__(*groups)

        self.pieces = Group()
        for ii, klass in enumerate([Pawn, King, Queen, Bishop, Knight, Rook]):
            self.pieces.add(klass(100*(ii+1), 100*(ii+1)))
        # initialise engine board
        # initialise visual board
        # initialise visual pieces

        self.child_groups = [self.pieces]
