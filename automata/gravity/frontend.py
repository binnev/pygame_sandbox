import pygame.draw
from pygame import Surface, Color, Rect

from automata.frontend import Transform
from automata.gravity.automaton import GravityAutomaton
from automata.viewport_handler import FloatRect


class GravityFrontend:
    def draw(
        self,
        surface: Surface,
        automaton: GravityAutomaton,
        viewport: FloatRect,
        debug: bool = False,
    ):
        """
        For now just draw everything
        """
        surface.fill(Color("black"))

        viewport_rect_xy = Rect(*viewport).inflate(2, 2)
        visible = {
            (x, y): body
            for (x, y), body in automaton.contents.items()
            # if viewport_rect_xy.collidepoint(x, y)
            if viewport_rect_xy.colliderect(
                Rect(x - body.radius, y - body.radius, body.radius * 2, body.radius * 2)
            )
        }

        image_rect_uv = surface.get_rect()
        transform = Transform(viewport, image_rect_uv)

        for xy, body in visible.items():
            color = self.get_color(body)
            uv = transform.point(xy)
            radius = body.radius * transform.scale
            pygame.draw.circle(surface, color, center=uv, radius=radius)

    def get_color(self, body):
        return Color("red")
