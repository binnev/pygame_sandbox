import math
import string
from collections.abc import Callable

import pygame
from pygame import Surface, Rect, Color

from base.animation import ease_in, ease_out
from base.gui.menu import Menu
from base.input import EventQueue
from base.objects import Entity, Group
from base.text.font import fonts, Font
from dinosaur_jump import conf, images
from dinosaur_jump.score import highscores_table, Score


class FlyingGuiMixin(Entity):
    start_x: int
    start_y: int
    target_x: int
    target_y: int
    state_idle: Callable
    animation_duration: int = 15

    def __init__(self):
        super().__init__()
        self.state = self.state_animate_in

    def state_animate_in(self):
        self.y = ease_out(start=self.start_y, stop=self.target_y, num=self.animation_duration)[
            self.tick
        ]
        if self.tick == self.animation_duration - 1:
            self.state = self.state_idle

    def state_animate_out(self):
        self.y = ease_in(start=self.target_y, stop=self.start_y, num=self.animation_duration)[
            self.tick
        ]
        if self.tick == self.animation_duration - 1:
            self.kill()

    def state_idle(self):
        pass

    def exit(self):
        self.state = self.state_animate_out


class Toast(FlyingGuiMixin):
    def __init__(self, text, y=10, from_above=True, font=fonts.cellphone_white, **font_params):
        super().__init__()
        self.from_above = from_above
        self.target_y = y
        self.start_y = -35 if from_above else conf.WINDOW_HEIGHT + 20
        self.text = text
        self.font = font
        self.font_params = font_params

    def draw(self, surface: Surface, debug: bool = False):
        params = dict(wrap=conf.WINDOW_WIDTH, align=0, scale=5)
        params.update(self.font_params)
        self.font.render(surface, text=self.text, x=0, y=self.y, **params)


class DinoMenu(Menu):
    def exit(self):
        for group in self.child_groups:
            for entity in group:
                if hasattr(entity, "exit"):
                    entity.exit()
                else:
                    entity.kill()
        self.state = self.state_exit

    def state_exit(self):
        """Die when all entities have finished animating out"""
        if not any(self.child_groups):
            self.kill()


class PauseMenu(DinoMenu):
    def __init__(self):
        super().__init__()
        self.entities = Group()
        self.child_groups += [self.entities]
        self.entities.add(Toast("PAUSED", from_above=False))
        self.entities.add(Toast("Controls:", y=100, from_above=False))
        self.entities.add(Key(x=100, y=100, character="F"))
        self.entities.add(Key(x=100, y=200, character="Space"))


class GameOverMenu(DinoMenu):
    def __init__(self, score: int):
        super().__init__()
        self.score = score
        self.entities = Group()
        self.child_groups += [self.entities]
        self.entities.add(Toast("R.I.P.", scale=10))
        self.entities.add(Toast(f"Score: {score}", y=100))
        self.entities.add(Toast("PRESS SPACE TO CONTINUE", y=150))
        self.text_field = TextField(
            initial_text="Enter your name",
            x=conf.WINDOW_WIDTH // 2 - 150,
            y=200,
            width=300,
            height=50,
            font=fonts.cellphone_white,
            scale=5,
        )
        self.entities.add(self.text_field)
        self.entities.add(Toast("Highscores", y=250, from_above=False))
        self.entities.add(
            Toast(
                highscores_table(),
                y=300,
                from_above=False,
                font=fonts.cellphone_white_mono,
                scale=3,
                align=0,
            )
        )

    def exit(self):
        super().exit()
        name = self.text_field.text.strip() or "anonymous"
        Score(score=self.score, name=name).save()


class TextField(Entity):
    ALLOWED_CHARS = (
        string.ascii_uppercase + string.ascii_lowercase + string.digits + string.punctuation + "-_"
    )
    cursor_blink_speed = 30

    def __init__(self, x, y, width, height, font: Font, initial_text: str, **font_kwargs) -> None:
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.rect = Rect((x, y, width, height))
        self.initial_text = initial_text
        self.text = ""
        self.state = self.state_active
        self.font_kwargs = font_kwargs
        self.draw_cursor = True

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        pygame.draw.rect(surface, Color("gray"), self.rect, 5)
        cursor_x = self.font.render(
            surface,
            self.text,
            x=self.x + 10,
            y=self.y,
            **self.font_kwargs,
        )
        if not self.text:
            self.font.render(
                surface,
                self.initial_text,
                x=self.x + 10,
                y=self.y,
                **self.font_kwargs,
            )
        if self.draw_cursor:
            pygame.draw.rect(surface, Color("white"), (cursor_x, self.y, 2, 50), 5)

    def state_active(self):
        if self.tick % self.cursor_blink_speed == 0:
            self.draw_cursor = not self.draw_cursor
        if event := EventQueue.get(type=pygame.KEYDOWN):
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode in self.ALLOWED_CHARS:
                self.text += event.unicode

    def exit(self):
        self.kill()


class Key(Entity):
    def __init__(self, x, y, character: str):
        super().__init__()
        self.x = x
        self.y = y
        self.font = fonts.cellphone_black
        self.character = character

        text_width = self.font.printed_width(self.character, scale=5)
        n_mid = math.ceil(text_width / images.keycap_mid.get_width())
        self.parts = [images.keycap_left] + [images.keycap_mid] * n_mid + [images.keycap_right]
        total_width = sum(part.get_width() for part in self.parts)
        self.image = Surface((total_width, images.keycap_mid.get_height())).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        x = 0
        for image in self.parts:
            self.image.blit(image, (x, 0))
            x += image.get_width()
        self.font.render(
            surf=self.image,
            text=self.character,
            x=0,
            y=10,
            scale=5,
            wrap=total_width,
            align=0,
        )

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        surface.blit(self.image, (self.x, self.y))
