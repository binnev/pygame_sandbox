from base.objects import Entity, Group
from chess.gui.classes.board import GuiBoard


class ChessMatch(Entity):
    def __init__(self, *groups):
        super().__init__(*groups)

        self.boards = Group()
        self.boards.add(GuiBoard())
        self.child_groups = [self.boards]
