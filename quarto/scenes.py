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

        # self.entities.add(
        #     QuartoBoard(),
        #     PieceSideArea(),
        #     NextPiecePillow(),
        # )
        ii = 0
        for tall in True, False:
            for hollow in True, False:
                for square in True, False:
                    for black in True, False:
                        x, y = divmod(ii, 4)
                        self.entities.add(
                            Piece(
                                100 * x + 100,
                                100 * y + 200,
                                tall=tall,
                                hollow=hollow,
                                square=square,
                                black=black,
                            ),
                        )
                        ii += 1
