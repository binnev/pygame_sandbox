import pygame.mouse

from base.animation import damping_response
from base.examples.gui_examples.assets import flashy_button_sprites
from base.gui.button import Button
from base.image import scale_image, brighten, SpriteAnimation
from base.objects import Game, Group, Particle
from base.utils import mouse_hovering_over, random_int


class ButtonWithImages(Button):
    sprites = flashy_button_sprites
    frame_duration = 3

    def __init__(self, x: int, y: int, width: int, height: int, **kwargs):
        super().__init__(x, y, width, height, **kwargs)
        self.image_idle = self.sprites.flash.play(0)
        self.image_pressed = brighten(scale_image(self.image_idle.copy(), 0.9), amount=30)
        sizes = [damping_response(t) for t in range(30)]
        images = [scale_image(self.image_idle.copy(), s) for s in sizes]
        self.animation_on_release = SpriteAnimation(images=images)
        self.animation = SpriteAnimation(images=[self.image_idle])

    def state_idle(self):
        super().state_idle()
        self.image = self.animation.play_once(self.animation_frame)

    def state_focus(self):
        super().state_focus()
        self.image = self.animation.play_once(self.animation_frame)

    def state_press(self):
        super().state_press()
        self.image = self.animation_on_release.play(0)

    def on_focus(self):
        super().on_focus()
        self.animation = self.sprites.flash

    def on_release(self):
        super().on_release()
        self.animation = self.animation_on_release


class ColoredButtonEffectsExample(Game):
    """
    This is an example where the Buttons have different colours/animations for each state and
    transition.
    """

    screen_color = (50, 50, 50)

    def __init__(self):
        super().__init__()
        self.buttons = Group()
        self.particles = Group()
        self.child_groups += [self.buttons, self.particles]
        self.buttons.add(
            ButtonWithImages(
                x=200,
                y=100,
                width=200,
                height=100,
                text="press and hold for smoke",
                on_release=(
                    lambda button: (
                        self.particles.add(Flash(x=button.x, y=button.y)),
                        self.particles.add(Glow(x=button.x, y=button.y) for _ in range(10)),
                    )
                ),
                on_unfocus=(lambda button: self.particles.kill()),
            )
        )

    def update(self):
        super().update()

        # button manager stuff
        for button in self.buttons:
            if mouse_hovering_over(button):
                button.is_focused = True
                button.is_pressed = pygame.mouse.get_pressed()[0]
            else:
                button.is_focused = False
                button.is_pressed = False


class Flash(Particle):
    gravity = 0.1
    friction = 0.01
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
    ColoredButtonEffectsExample().main()
