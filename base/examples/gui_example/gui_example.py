import pygame.mouse
from pygame import Color
from pygame.event import Event

from base.gui.button import Button
from base.input import EventQueue
from base.objects import Game, Group, Particle
from base.utils import mouse_hovering_over, random_int


class events:
    INCREMENT_VALUE = pygame.event.custom_type()


class GuiExample(Game):
    screen_color = (50, 50, 50)

    def __init__(self):
        super().__init__()
        self.value = 0
        self.buttons = Group()
        self.particles = Group()
        self.child_groups += [self.buttons, self.particles]
        self.buttons.add(
            Button(
                x=100,
                y=100,
                width=100,
                height=50,
                text="up",
                on_press=(
                    lambda button: (
                        EventQueue.add(Event(events.INCREMENT_VALUE)),
                        self.particles.add(Flash(x=button.x, y=button.y)),
                        [self.particles.add(Glow(x=button.x, y=button.y)) for _ in range(10)],
                    )
                ),
                on_focus=(lambda button: print("on_focus")),
                on_unfocus=(lambda button: print("on_unfocus")),
                on_release=(lambda button: print("on_release")),
            )
        )

    def update(self):
        super().update()
        if EventQueue.get(type=events.INCREMENT_VALUE):
            self.value += 1
        print(f"{self.value=}")

        # doing button manager stuff here
        for button in self.buttons:
            if mouse_hovering_over(button):
                button.is_focused = True
                button.is_pressed = pygame.mouse.get_pressed()[0]
            else:
                button.is_focused = False
                button.is_pressed = False


class Flash(Particle):
    gravity = 0.1
    friction = 0.1
    decay = 20
    color = (150, 200, 150)
    radius = 100


class Glow(Particle):
    gravity = 0.1
    friction = 0.1
    decay = 0.1
    color = (20, 20, 20)
    radius = 50

    def __init__(self, x, y):
        super().__init__(x, y, u=random_int(-5, 5), v=random_int(-5, 5))


if __name__ == "__main__":
    GuiExample().main()
