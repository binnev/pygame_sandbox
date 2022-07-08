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
        self.image = self.image_idle

    def state_idle(self):
        self.image = self.image_idle
        super().state_idle()

    def state_focus(self):
        self.image = self.animation.play_once(self.animation_frame, repeat_frame=0)
        super().state_focus()

    def state_press(self):
        self.image = self.image_pressed
        super().state_press()

    def on_focus(self):
        super().on_focus()
        self.animation = self.sprites.flash

    def on_release(self):
        super().on_release()
        self.animation = SpriteAnimation(images=[self.image_idle])


class BouncyButton(Button):
    sprites = flashy_button_sprites
    frame_duration = 3

    def __init__(self, x: int, y: int, width: int, height: int, **kwargs):
        super().__init__(x, y, width, height, **kwargs)
        self.image = self.sprites.flash.play(0)
        sizes = [damping_response(t) for t in range(20)]
        self.animation = self.sprites.flash
        self.animation_timer = 99
        self.physics_timer = 0
        self.amplitude = 0

    def on_press(self):
        super().on_press()
        self.physics_timer = 0
        self.amplitude = -0.4

    def on_focus(self):
        super().on_focus()
        self.animation_timer = 0
        self.physics_timer = 0
        self.amplitude = 0.1

    def update(self):
        super().update()
        self.image = self.animation.play_once(
            self.animation_timer // self.frame_duration, repeat_frame=0
        )
        scale_factor = damping_response(self.physics_timer, amp=self.amplitude)
        if abs(scale_factor) > 0.01:
            self.image = scale_image(self.image.copy(), 1 + scale_factor)
        self.physics_timer += 1
        self.animation_timer += 1


class ColoredButtonEffectsExample(Game):
    """
    This is an example where the Buttons have different colours/animations for each state and
    transition.
    """

    screen_color = (50, 50, 50)
    window_width = 500
    window_height = 500

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
            ),
            BouncyButton(x=200, y=300, width=200, height=100),
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
