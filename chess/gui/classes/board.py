import pygame
from pygame import Surface, Color
from pygame.rect import Rect

from base.input import EventQueue
from base.objects import Entity, PhysicalEntity, Group
from base.stuff.gui_test import mouse_hovering_over
from chess import conf, sounds
from chess.constants import KNIGHT, QUEEN, ROOK, BISHOP
from chess.engine.classes.board import ChessBoard
from chess.engine.classes.move import Move
from chess.gui.classes.piece import GuiPiece
from chess.gui.utils import distance
from chess.utils import other_team


class GuiSquare(PhysicalEntity):
    width = conf.SQUARE_SIZE
    height = conf.SQUARE_SIZE
    color: Color

    def __init__(self, x, y, coords, color: Color, *groups):
        """
        :param x: screen x
        :param y: screen y
        :param coords: coordinates for the engine
        :param groups:
        """
        super().__init__(*groups)
        self.rect = Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.color = color
        self.coords = coords

    @property
    def image(self):
        image = Surface((self.width - 5, self.height - 5))
        if mouse_hovering_over(self):
            image.fill((160, 160, 130))
        else:
            image.fill(self.color)

        # font = pygame.font.Font(pygame.font.get_default_font(), 20)
        # text = font.render(f"{self.coords[0]}, {self.coords[1]}", True, Color("red"))
        # textRect = text.get_rect()
        # textRect.bottomleft = image.get_rect().bottomleft
        # image.blit(text, textRect)

        return image


class SquareAnnotation(PhysicalEntity):
    width = conf.SQUARE_SIZE
    height = conf.SQUARE_SIZE
    color: Color = (30, 30, 30, 30)

    def __init__(self, x, y, *groups):
        super().__init__(*groups)
        self.rect = Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        pygame.draw.circle(surface, self.color, self.rect.center, conf.SQUARE_SIZE // 3, 5)


class GuiBoard(Entity):
    parental_name = "board"

    def __init__(self, *groups):
        super().__init__(*groups)
        self.squares = Group()
        self.pieces = Group()
        self.selected_pieces = Group()
        self.annotations = Group()
        self.child_groups = [
            self.squares,
            self.annotations,
            self.pieces,
            self.selected_pieces,
        ]
        self.state = self.state_idle
        self.square_coords = dict()

        for x in range(8):
            for y in range(8):
                color = (40, 40, 40) if (y % 2) == (x % 2) else (90, 90, 90)
                screen_x = (x + 1) * conf.SQUARE_SIZE
                screen_y = conf.SQUARE_SIZE * 10 - (y + 1) * conf.SQUARE_SIZE
                square = GuiSquare(screen_x, screen_y, (x, y), color)
                self.add_squares(square)
                self.square_coords[(x, y)] = square

        self.engine = ChessBoard()
        self.engine.load_standard_setup()
        self.load_engine_position()

    def load_engine_position(self):
        self.pieces.kill()
        self.selected_pieces.kill()
        for coords, engine_piece in self.engine.position.items():
            # todo: use engine piece coords too.
            piece = GuiPiece(0, 0, engine_piece.team, type=engine_piece.type)
            self.add_piece_to_square(piece, coords)

    def add_piece_to_square(self, piece, coords):
        square = self.square_coords[coords]
        piece.rect.center = square.rect.center
        piece.square = square
        self.add_pieces(piece)

    def add_squares(self, *objects):
        self.add_to_group(*objects, group=self.squares)

    def add_pieces(self, *objects):
        self.add_to_group(*objects, group=self.pieces)

    def add_annotations(self, *objects):
        self.add_to_group(*objects, group=self.annotations)

    def pick_up(self, piece: GuiPiece):
        self.annotations.kill()
        piece.state = piece.state_grabbed
        self.selected_pieces.add(piece)
        self.pieces.remove(piece)
        # add annotations for piece's legal moves
        annotations = []
        for move in self.engine.get_moves(piece.square.coords):
            square = self.square_coords[move.destination]
            annotation = SquareAnnotation(square.x, square.y)
            annotations.append(annotation)
        self.add_annotations(*annotations)

    def put_down(self, piece: GuiPiece):
        new_square = min(self.squares, key=lambda s: distance(s, piece))

        # check move is legal
        legal_moves = self.engine.get_moves(piece.square.coords)
        legal_moves = {move for move in legal_moves if move.destination == new_square.coords}
        if legal_moves:
            move = legal_moves.pop()  # todo: promotion will require a menu
            self.engine.do_move(move)
            print(self.engine)
            self.do_move(move)

        else:
            piece.animate_to(
                xy=piece.square.rect.center,
                next_state=piece.state_idle,
                duration_ticks=10,
            )
            self.selected_pieces.remove(piece)
            self.pieces.add(piece)

    def remove(self, piece: GuiPiece):
        self.engine.position.pop(piece.square.coords)
        piece.kill()

    def state_idle(self):
        if EventQueue.get(type=pygame.MOUSEBUTTONDOWN, button=pygame.BUTTON_LEFT):
            for piece in self.pieces:
                if mouse_hovering_over(piece):
                    self.pick_up(piece)
                    break  # only one piece at a time

        if EventQueue.get(type=pygame.MOUSEBUTTONDOWN, button=pygame.BUTTON_RIGHT):
            for piece in self.pieces:
                if mouse_hovering_over(piece):
                    self.remove(piece)
                    break  # only one piece at a time

        if EventQueue.filter(type=pygame.MOUSEBUTTONUP):
            for piece in self.selected_pieces:
                self.put_down(piece)

        if EventQueue.filter(type=pygame.KEYDOWN, key=pygame.K_LEFT):
            last_move = self.engine.move_history[-1]
            self.undo_move(last_move)
            self.engine.back()
            # self.load_engine_position()

    def undo_move(self, move: Move):
        piece = next(piece for piece in self.pieces if piece.square.coords == move.destination)

    def do_move(self, move: Move):
        piece = next(piece for piece in self.selected_pieces if piece.square.coords == move.origin)
        target_square = next(square for square in self.squares if square.coords == move.destination)

        # animate piece to new square
        piece.animate_to(xy=target_square.rect.center)
        piece.square = target_square
        self.selected_pieces.remove(piece)
        self.pieces.add(piece)

        # promotion
        if move.promote_to:
            new_piece = GuiPiece(*piece.rect.center, team=piece.team, type=move.promote_to)
            new_piece.square = piece.square
            new_piece.animate_to(xy=new_piece.square.rect.center)
            self.pieces.add(new_piece)
            piece.kill()
            piece = new_piece

        if move.captured_piece:
            captured_piece = next(
                piece for piece in self.pieces if piece.square.coords == move.captured_piece_square
            )
            captured_piece.blood()
            captured_piece.kill()

        if move.extra_move:
            self.do_move(move.extra_move)

        if self.engine.is_checkmated(other_team(piece.team)):
            sounds.checkmate.play()
        elif self.engine.is_in_check(other_team(piece.team)):
            sounds.check.play()
        elif self.engine.is_stalemated(other_team(piece.team)):
            sounds.stalemate.play()

        self.annotations.kill()
