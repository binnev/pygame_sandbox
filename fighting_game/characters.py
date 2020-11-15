from fighting_game.objects import *

class Debugger(Character):
    mass = 10  # 10 is average
    width = 50
    height = 100
    color = Color("cyan")
    ground_acceleration = 99
    ground_speed = 7
    air_acceleration = 0.75
    air_speed = 5
    gravity = 0.3
    jump_power = 10
    air_resistance = 0.1
    friction = 1
    fall_speed = 7

    def __init__(self, x, y, input=FightingGameInput, facing_right=True):
        super().__init__(x, y, input, facing_right)
        self.state = self.state_fall
        self.sprites = stickman_sprites()
        self.damage = 0

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)

        def tprint(surface, x, y, textString):
            font = pygame.font.Font(None, 30)
            textBitmap = font.render(textString, True, Color("black"))
            surface.blit(textBitmap, (x, y))

        colliding = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
        touching = [plat for plat in self.level.platforms if self.touching(plat)]
        try:
            state_name = self.state.__name__
        except AttributeError:
            state_name = self.state.__class__.__name__
        things_to_print = [
            f"u = {self.u}",
            f"v = {self.v}",
            f"airborne = {self.airborne}",
            f"touching: {touching}",
            f"colliding: {colliding}",
            f"state: {state_name}",
            f"damage: {self.damage}%",
        ]
        line_spacing = 20
        for ii, thing in enumerate(things_to_print):
            tprint(
                surface,
                self.rect.left,
                self.rect.top + ii * line_spacing - line_spacing * len(things_to_print),
                thing,
            )


class Debugger2(Debugger):
    mass = 8
