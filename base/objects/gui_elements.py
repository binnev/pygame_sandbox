import pygame

from base.objects.entities import Entity


class GuiButton(Entity):
    def __init__(self, *args, **kwargs):
        self.text = kwargs.pop("text", None)
        self.text_color = kwargs.pop("text_color", None)
        if not self.text_color:
            self.text_color = self.debug_color
        super().__init__(*args, **kwargs)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)

    def draw_image(self, surface):
        if self.text:
            text = self.font.render(self.text, True, self.text_color)
            textRect = text.get_rect()
            textRect.center = self.image.get_rect().center
            self.image.blit(text, textRect)
        super().draw_image(surface)
