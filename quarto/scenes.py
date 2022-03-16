from typing import TYPE_CHECKING

from pygame.sprite import AbstractGroup

from base.objects import Entity, Group
from quarto.objects import Piece

if TYPE_CHECKING:
    from quarto.game import QuartoGame


class QuartoMatch(Entity):
    game: "QuartoGame"

    def __init__(self, *groups: AbstractGroup) -> None:
        super().__init__(*groups)

        self.entities = Group()
        self.child_groups = [self.entities]

        self.entities.add(
            # QuartoBoard(),
            # PieceSideArea(),
            # NextPiecePillow(),
            Piece(100, 100)
        )
