from typing import TYPE_CHECKING

import pygame
from pygame import Surface, Color
from pygame.rect import Rect

from base.image import recolor_image
from base.animation import ease_in_out
from base.objects import PhysicalEntity, Group
from base.stuff.gui_test import mouse_hovering_over
from chess import conf
from chess.assets.pieces import chess_pieces
from chess.constants import WHITE, BLACK, Teams, PieceTypes
from fighting_game.particles import random_float, Particle, random_int

if TYPE_CHECKING:
    from chess.gui.classes.board import GuiBoard, GuiSquare


class GuiPiece(PhysicalEntity):
    letter: str
    team: str
    width = conf.SQUARE_SIZE
    height = conf.SQUARE_SIZE
    sprite_name: str
    board: "GuiBoard"
    square: "GuiSquare"

    def __init__(self, x, y, team: Teams, type=PieceTypes, *groups):
        super().__init__(*groups)
        self.team = team
        self.type = type
        self.rect = Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.image = chess_pieces[self.type].play(0)
        if self.team != WHITE:
            self.image = recolor_image(
                self.image,
                {
                    (255, 255, 255): Color("black"),
                    (0, 0, 0): Color("white"),
                },
            )
        self.state = self.state_idle
        self.particles = Group()
        self.child_groups = [self.particles]

    def draw(self, surface: Surface, debug: bool = False):
        # todo: this is to make child particles appear behind self. Need to make it so I can
        #  configure this without hacking.
        super().draw(surface, debug)
        surface.blit(self.image, self.image_rect)

    def state_idle(self):
        if mouse_hovering_over(self):
            self.smoke()

    def state_grabbed(self):
        self.flame()
        self.rect.center = pygame.mouse.get_pos()

    def animate_to(self, xy, duration_ticks=10, next_state=None):
        next_state = next_state or self.state_idle
        x0, y0 = self.rect.center
        x1, y1 = xy
        xs = (x for x in ease_in_out(x0, x1, duration_ticks))
        ys = (y for y in ease_in_out(y0, y1, duration_ticks))

        def state_animate():
            try:
                x = next(xs)
                y = next(ys)
                self.rect.center = (x, y)
            except StopIteration:
                self.state = next_state

        self.state = state_animate

    def spark(self):
        for _ in range(20):
            self.particles.add(
                Particle(
                    x=self.x + random_int(-5, 5),
                    y=self.y + random_int(-5, 5),
                    u=1 * random_float(-15, 15),
                    v=1 * random_float(-15, 15),
                    radius=random_int(5, 12),
                    color=(200, 200, 150),
                    gravity=0.1,
                    decay=0.2,
                    friction=0.1,
                )
            )

    def blood(self):
        for _ in range(20):
            self.particles.add(
                Particle(
                    x=self.x + random_int(-5, 5),
                    y=self.y + random_int(-5, 5),
                    u=1 * random_float(-15, 15),
                    v=1 * random_float(-15, 15),
                    radius=random_int(5, 12),
                    color=(255, 0, 0),
                    gravity=0.1,
                    decay=0.2,
                    friction=0.1,
                )
            )

    def smoke(self):
        self.particles.add(
            Particle(
                self.x + random_float(-15, 15),
                self.y + random_float(-15, 15),
                u=0 + random_float(-1, 1),
                v=-3 + random_float(-5, 5),
                radius=random_int(12, 25),
                color=self.flame_color,
                gravity=-0.02,
                friction=0.025,
                blit_flag=pygame.BLEND_SUB,
                decay=1.5,
            )
        )

    @property
    def flame_color(self):
        return (
            (
                random_int(0, 80),
                random_int(0, 15),
                random_int(0, 100),
            )
            if self.team == BLACK
            else (
                random_int(0, 60),
                random_int(0, 60),
                random_int(0, 10),
            )
        )

    def flame(self):
        self.particles.add(
            Particle(
                self.x,
                self.y,
                u=30 * 0 + random_float(-5, 5),
                v=30 * 0 + random_float(-5, 5),
                radius=random_int(30, 60),
                color=self.flame_color,
                gravity=-0.5,
                decay=1,
                friction=0.1,
                blit_flag=pygame.BLEND_SUB,
            )
        )
