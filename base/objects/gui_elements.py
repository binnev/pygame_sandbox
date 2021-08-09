import pygame
from pygame.color import Color

from base.objects.entities import Entity
from base.utils import mask_to_surface


class GuiButton(Entity):
    # These attributes are set by whatever is managing the buttons. The button itself doesn't
    # check these.
    focus: bool  # is the mouse hovering over the button at the moment?
    click: bool  # is the button currently being clicked?
    debug_color = (0, 100, 100)

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text=None,
        text_color=None,
        on_click: "callback" = None,
        on_focus: "callback" = None,
        **kwargs
    ):
        self.text = text
        self.text_color = text_color or self.debug_color
        super().__init__(x=x, y=y, width=width, height=height, **kwargs)
        self.current_color = self.color
        self.focus = False
        self.click = False
        self.highlight = False
        self.on_click = on_click or (lambda: None)
        self.on_focus = on_focus or (lambda: None)

    @property
    def image(self):
        image = pygame.Surface((self.width, self.height)).convert_alpha()
        image.fill(self.current_color)
        if self.text:
            text = self.font.render(self.text, True, self.text_color)
            textRect = text.get_rect()
            textRect.center = image.get_rect().center
            image.blit(text, textRect)
        return image

    def draw(self, surface, debug=False):
        super().draw(surface, debug)
        if self.highlight:
            self.draw_highlight(surface)

    def draw_highlight(self, surface):
        color = pygame.color.THECOLORS["brown"]  # todo: make highlight color
        translucent_color = color[:3] + (50,)
        mask_surface = mask_to_surface(self.mask, translucent_color)
        mask_outline = self.mask.outline()
        pygame.draw.polygon(mask_surface, color, mask_outline, 15)
        surface.blit(mask_surface, self.image_rect)

    def update(self):
        self.current_color = self.color
        self.highlight = False

        if self.focus:
            self._own_on_focus()
            self.on_focus()

        if self.click:
            self._own_on_click()
            self.on_click()

        super().update()

    def _own_on_focus(self):
        """The button's own logic that is executed when the button has focus. Not to be confused
        with self.on_focus which will be a callback passed by the creator of the button."""
        self.highlight = True

    def _own_on_click(self):
        """ Button's own logic for when clicked. """
        self.current_color = Color("red")
