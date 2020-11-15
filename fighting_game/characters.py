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


    class AttackMove(Move):
        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                width=70,
                height=50,
                rotation=30,
                base_knockback=10,
                knockback_angle=90,
                knockback_growth=20,
                damage=20,
            )
            sour_spot = Hitbox(
                owner=character,
                width=150,
                height=100,
                rotation=45,
                base_knockback=5,
                knockback_angle=90,
                knockback_growth=10,
                damage=10,
                higher_priority_sibling=sweet_spot,
            )
            assert sour_spot.higher_priority_sibling is sweet_spot
            assert sweet_spot.lower_priority_sibling is sour_spot
            self.hitbox_mapping = {
                (1, 3): [sweet_spot],
                (4, 6): [sweet_spot, sour_spot],
                (7, 10): [sour_spot],
            }
            super().__init__(character)

        def __call__(self):
            super().__call__()
            character = self.character
            if character.animation_frame == 11:
                character.state = character.state_stand

    class ForwardAir(Move):
        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                x_offset=30,
                width=30,
                height=30,
                rotation=0,
                base_knockback=10,
                knockback_angle=1,
                knockback_growth=20,
                damage=20,
            )
            sour_spot = Hitbox(
                owner=character,
                x_offset=30,
                width=20,
                height=20,
                rotation=0,
                base_knockback=5,
                knockback_angle=1,
                knockback_growth=10,
                damage=10,
                higher_priority_sibling=sweet_spot,
            )
            assert sour_spot.higher_priority_sibling is sweet_spot
            assert sweet_spot.lower_priority_sibling is sour_spot
            self.hitbox_mapping = {
                (1, 3): [sweet_spot],
                (4, 6): [sweet_spot, sour_spot],
                (7, 10): [sour_spot],
            }
            super().__init__(character)

        def __call__(self):
            super().__call__()
            character = self.character
            if character.animation_frame == 11:
                character.state = character.state_stand

    class BackAir(Move):
        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                x_offset=-30,
                width=30,
                height=30,
                rotation=0,
                base_knockback=10,
                knockback_angle=180,
                knockback_growth=20,
                damage=20,
            )
            sour_spot = Hitbox(
                owner=character,
                x_offset=-30,
                width=20,
                height=20,
                rotation=0,
                base_knockback=5,
                knockback_angle=180,
                knockback_growth=10,
                damage=10,
                higher_priority_sibling=sweet_spot,
            )
            assert sour_spot.higher_priority_sibling is sweet_spot
            assert sweet_spot.lower_priority_sibling is sour_spot
            self.hitbox_mapping = {
                (1, 3): [sweet_spot],
                (4, 6): [sweet_spot, sour_spot],
                (7, 10): [sour_spot],
            }
            super().__init__(character)

        def __call__(self):
            super().__call__()
            character = self.character
            if character.animation_frame == 11:
                character.state = character.state_stand

    class UpAir(Move):
        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                y_offset=-30,
                width=30,
                height=30,
                rotation=0,
                base_knockback=10,
                knockback_angle=90,
                knockback_growth=20,
                damage=20,
            )
            sour_spot = Hitbox(
                owner=character,
                y_offset=-30,
                width=20,
                height=20,
                rotation=0,
                base_knockback=5,
                knockback_angle=90,
                knockback_growth=10,
                damage=10,
                higher_priority_sibling=sweet_spot,
            )
            assert sour_spot.higher_priority_sibling is sweet_spot
            assert sweet_spot.lower_priority_sibling is sour_spot
            self.hitbox_mapping = {
                (1, 3): [sweet_spot],
                (4, 6): [sweet_spot, sour_spot],
                (7, 10): [sour_spot],
            }
            super().__init__(character)

        def __call__(self):
            super().__call__()
            character = self.character
            if character.animation_frame == 11:
                character.state = character.state_stand

    class DownAir(Move):
        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                y_offset=30,
                width=30,
                height=30,
                rotation=0,
                base_knockback=10,
                knockback_angle=270,
                knockback_growth=20,
                damage=20,
            )
            sour_spot = Hitbox(
                owner=character,
                y_offset=30,
                width=20,
                height=20,
                rotation=0,
                base_knockback=5,
                knockback_angle=270,
                knockback_growth=10,
                damage=10,
                higher_priority_sibling=sweet_spot,
            )
            assert sour_spot.higher_priority_sibling is sweet_spot
            assert sweet_spot.lower_priority_sibling is sour_spot
            self.hitbox_mapping = {
                (1, 3): [sweet_spot],
                (4, 6): [sweet_spot, sour_spot],
                (7, 10): [sour_spot],
            }
            super().__init__(character)

        def __call__(self):
            super().__call__()
            character = self.character
            if character.animation_frame == 11:
                character.state = character.state_stand

    class NeutralAir(Move):
        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                y_offset=30,
                width=30,
                height=30,
                rotation=0,
                base_knockback=10,
                knockback_angle=80,
                knockback_growth=10,
                damage=20,
            )
            sour_spot = Hitbox(
                owner=character,
                y_offset=30,
                width=20,
                height=20,
                rotation=0,
                base_knockback=5,
                knockback_angle=80,
                knockback_growth=5,
                damage=10,
                higher_priority_sibling=sweet_spot,
            )
            assert sour_spot.higher_priority_sibling is sweet_spot
            assert sweet_spot.lower_priority_sibling is sour_spot
            self.hitbox_mapping = {
                (1, 3): [sweet_spot],
                (4, 6): [sweet_spot, sour_spot],
                (7, 10): [sour_spot],
            }
            super().__init__(character)

        def __call__(self):
            super().__call__()
            character = self.character
            if character.animation_frame == 11:
                character.state = character.state_stand

class Debugger2(Debugger):
    mass = 8
