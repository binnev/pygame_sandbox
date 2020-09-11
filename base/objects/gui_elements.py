import pygame

from base.objects.entities import Entity
from base.utils import mask_to_surface


class GuiButton(Entity):
    """
    todo: even something as simple as a button must be a state machine. Perhaps I should build
    the state machine functionality into Entity? If I want a button to do an animation on hover (
    instead of just showing its outline) then I need a state to handle that animation.

    todo: Perhaps I should unify Entity and AnimationMixin. Animationmixin explicitly uses
    self.state to set self.frames elapsed etc. I think I can also improve the way states are
    defined. Perhaps I can use the factory method to register states. Also, AnimationMixin should
    use self.current_animation to draw frames from. Then states can set current_animation.

    todo: implement passing "on_click" callbacks.
    """

    # These attributes are set by whatever is managing the buttons. The button itself doesn't
    # check these.
    focus: bool  # is the mouse hovering over the button at the moment?
    clicked: bool  # is the button currently being clicked?

    def __init__(self, *args, **kwargs):
        self.text = kwargs.pop("text", None)
        self.text_color = kwargs.pop("text_color", None)
        if not self.text_color:
            self.text_color = self.debug_color
        super().__init__(*args, **kwargs)

    @property
    def image(self):
        image = pygame.Surface((self.width, self.height)).convert_alpha()
        image.fill(self.color)
        if self.text:
            text = self.font.render(self.text, True, self.text_color)
            textRect = text.get_rect()
            textRect.center = image.get_rect().center
            image.blit(text, textRect)
        return image

    def draw(self, surface, debug=False):
        super().draw(surface, debug)
        if self.focus:
            self.draw_highlight(surface)

    def draw_highlight(self, surface):
        color = pygame.color.THECOLORS["brown"]
        translucent_color = color[:3] + (50,)
        mask_surface = mask_to_surface(self.mask, translucent_color)
        mask_outline = self.mask.outline()
        pygame.draw.polygon(mask_surface, color, mask_outline, 15)
        surface.blit(mask_surface, self.image_rect)

    def update(self):
        if self.focus and self.clicked:
            self.color = pygame.color.THECOLORS["green"]
        else:
            self.color = pygame.color.THECOLORS["red"]
        super().update()
