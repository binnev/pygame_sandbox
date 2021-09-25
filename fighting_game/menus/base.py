from random import random

import pygame
from pygame.color import Color
from pygame.rect import Rect

from base.animation import ease_in_out
from base.objects.gui_test import mouse_hovering_over, mouse_clicking
from base.utils import mask_to_surface
from fighting_game.conf import SCREEN_WIDTH, SCREEN_HEIGHT
from fighting_game.objects import Entity, Group, PhysicalEntity
from fighting_game.particles import Plume


class Menu(Entity):
    """ Base menu class. """

    parental_name = "menu"

    def __init__(self, *groups):
        super().__init__(*groups)
        self.buttons = Group()
        self.child_groups = [self.buttons]

    def add_button(self, *objects):
        self.add_to_group(*objects, group=self.buttons)

    def update(self):
        super().update()
        self.check_button_statuses()

    def check_button_statuses(self):
        for element in self.buttons:
            element.focus = mouse_hovering_over(element)
            element.click = mouse_clicking(element)

    def animate_to(self, animation_function, next_scene_callable):
        """Partial execution. State functions are called without any arguments, so if I want the
        animation function to know what state is next, I need to create this wrapper"""

        def wrapped():
            return animation_function(next_scene_callable)

        return wrapped


class Button(PhysicalEntity):
    # These attributes are set by whatever is managing the buttons. The button itself doesn't
    # check these.
    focus: bool  # is the mouse hovering over the button at the moment?
    click: bool  # is the button currently being clicked?
    debug_color = (0, 100, 100)
    font_name = "ubuntu"
    font_size = 20

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
        color=None,
    ):
        self.width = width
        self.height = height
        self.text = text
        self.text_color = text_color or self.debug_color
        self.rect = Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.color = color
        super().__init__()
        self.current_color = self.color
        self.focus = False
        self.click = False
        self.highlight = False
        self.on_click = on_click or (lambda: None)
        self.on_focus = on_focus or (lambda: None)
        self.font = pygame.font.Font(pygame.font.match_font(self.font_name), self.font_size)

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
        # mask_surface = mask_to_surface(self.mask, translucent_color)
        # mask_outline = self.mask.outline()
        # pygame.draw.polygon(mask_surface, color, mask_outline, 15)
        # surface.blit(mask_surface, self.image_rect)

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


class MainMenu(Menu):
    def __init__(self):
        super().__init__()
        self.state = self.animate_in
        self.explosion_button = Button(
            -999,
            200,
            200,
            50,
            text="random explosion",
            text_color=Color("white"),
            color=(100, 0, 100),
        )
        self.quit_button = Button(
            -999,
            400,
            200,
            50,
            text="quit",
            text_color=Color("white"),
            color=(100, 0, 100),
        )
        self.settings_button = Button(
            -999,
            300,
            200,
            50,
            text="settings",
            text_color=Color("white"),
            color=(100, 0, 100),
        )
        self.add_button(self.explosion_button, self.quit_button, self.settings_button)
        self.explosions = Group()
        self.child_groups.append(self.explosions)

    def animate_in(self):
        try:
            # todo: maybe make these generators so that you're not generating the entire array
            #  each tick
            xs = ease_in_out(-250, 250, 20)
            for button in self.buttons:
                button.x = xs[self.tick]
        except IndexError:
            self.state = self.idle

    def idle(self):
        if self.quit_button.click:
            self.state = self.animate_to(self.animate_out, None)
        if self.settings_button.click:
            self.game.add_scene(SettingsMenu())
            self.state = self.animate_to(self.animate_out, None)
        if self.explosion_button.click:
            self.explosions.add(
                Plume(
                    x=random() * SCREEN_WIDTH,
                    y=random() * SCREEN_HEIGHT,
                    angle_deg=random() * 360,
                )
            ),

    def animate_out(self, next_scene):
        try:
            xs = ease_in_out(250, 750, 20)
            for button in self.buttons:
                button.x = xs[self.tick]
        except IndexError:
            if next_scene:
                self.game.scenes.add(next_scene)
            self.kill()


class SettingsMenu(Menu):
    def __init__(self):
        super().__init__()
        self.state = self.animate_in
        self.back_button = Button(
            -999,
            200,
            200,
            50,
            text="back",
            text_color=Color("white"),
            color=(100, 0, 100),
        )
        self.buttons.add(self.back_button)

    def animate_in(self):
        try:
            xs = ease_in_out(-250, 250, 20)
            self.back_button.x = xs[self.tick]
        except IndexError:
            self.state = self.idle

    def idle(self):
        if self.back_button.click:
            self.game.add_scene(MainMenu())
            self.state = self.animate_to(self.animate_out, None)

    def animate_out(self, next_scene):
        try:
            xs = ease_in_out(250, 750, 20)
            self.back_button.x = xs[self.tick]
        except IndexError:
            if next_scene:
                self.game.scenes.add(next_scene)
            self.kill()
