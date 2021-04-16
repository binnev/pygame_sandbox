from fighting_game.objects import *


class Debugger(Character):
    mass = 10
    width = 50
    height = 100
    color = Color("cyan")
    ground_acceleration = 5
    walk_speed = 5
    run_speed = 9
    initial_dash_duration = 20
    run_turnaround_duration = 20
    air_acceleration = 0.75
    air_speed = 5
    gravity = 0.3
    jump_speed = 10
    shorthop_speed = 5
    air_resistance = 0.01
    friction = 0.3
    fall_speed = 7
    fast_fall_speed = 12
    jumpsquat_frames = 5

    def __init__(self, x, y, input=FightingGameInput, facing_right=True):
        super().__init__(x, y, input, facing_right)
        self.state = self.state_fall
        self.sprites = stickman_sprites()
        self.damage = 0

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        if not debug:
            return

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
            f"fast_fall: {self.fast_fall}",
            f"hitpause_duration: {self.hitpause_duration}",
        ]
        line_spacing = 20
        for ii, thing in enumerate(things_to_print):
            tprint(
                surface,
                self.rect.left,
                self.rect.top + ii * line_spacing - line_spacing * len(things_to_print),
                thing,
            )

    class ForwardAir(AerialMove):
        landing_lag = 5
        sound = sounds.sword_swing

        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                x_offset=30,
                width=30,
                height=30,
                rotation=45,
                base_knockback=10,
                knockback_angle=30,
                knockback_growth=20,
                damage=20,
                sound=sounds.sword_hit,
            )
            sour_spot = Hitbox(
                owner=character,
                x_offset=30,
                width=20,
                height=20,
                rotation=0,
                base_knockback=5,
                knockback_angle=45,
                knockback_growth=10,
                damage=10,
                higher_priority_sibling=sweet_spot,
                sound=sounds.sword_hit2,
            )
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
                character.state = character.state_fall

    class BackAir(AerialMove):
        landing_lag = 5

        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                x_offset=-30,
                width=30,
                height=30,
                rotation=0,
                base_knockback=10,
                knockback_angle=150,
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
                knockback_angle=135,
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
                character.state = character.state_fall

    class UpAir(AerialMove):
        landing_lag = 5

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
                character.state = character.state_fall

    class DownAir(AerialMove):
        landing_lag = 10

        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                y_offset=30,
                width=30,
                height=30,
                rotation=0,
                base_knockback=10,
                knockback_angle=280,
                knockback_growth=20,
                damage=20,
                sound=sounds.bighit,
            )
            sour_spot = Hitbox(
                owner=character,
                y_offset=30,
                width=20,
                height=20,
                rotation=0,
                base_knockback=5,
                knockback_angle=280,
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
                character.state = character.state_fall

    class NeutralAir(AerialMove):
        landing_lag = 5

        def __init__(self, character: Character):
            initial_hit = Hitbox(
                owner=character,
                width=50,
                height=50,
                rotation=0,
                base_knockback=40,
                knockback_angle=80,
                damage=5,
            )
            second_hit = Hitbox(
                owner=character,
                width=50,
                height=50,
                rotation=0,
                base_knockback=40,
                knockback_angle=80,
                damage=5,
            )
            final_hit = Hitbox(
                owner=character,
                width=50,
                height=50,
                rotation=0,
                base_knockback=5,
                knockback_angle=80,
                knockback_growth=5,
                damage=10,
            )
            self.hitbox_mapping = {
                (1, 2): [initial_hit],
                (4, 5): [second_hit],
                (7, 8): [final_hit],
            }
            super().__init__(character)

        def __call__(self):
            super().__call__()
            character = self.character
            if character.animation_frame == 10:
                character.state = character.state_fall

    class UpTilt(Move):
        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                y_offset=-30,
                width=60,
                height=60,
                rotation=0,
                base_knockback=30,
                knockback_angle=80,
                knockback_growth=5,
                damage=10,
            )
            self.hitbox_mapping = {
                (1, 3): [sweet_spot],
            }
            super().__init__(character)

        def __call__(self):
            super().__call__()
            character = self.character
            if character.animation_frame == 4:
                character.state = character.state_stand

    class Jab(Move):
        sound = sounds.swing3

        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                x_offset=10,
                y_offset=0,
                width=60,
                height=60,
                rotation=0,
                base_knockback=30,
                knockback_angle=45,
                knockback_growth=1,
                damage=10,
                sound=sounds.smack3,
            )
            self.hitbox_mapping = {
                (0, 2): [sweet_spot],
            }
            super().__init__(character)

        def __call__(self):
            super().__call__()
            character = self.character
            if character.animation_frame == 3:
                character.state = character.state_stand

    class DownSmash(Move):
        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                y_offset=30,
                width=60,
                height=60,
                rotation=0,
                base_knockback=10,
                knockback_angle=290,
                knockback_growth=20,
                damage=20,
                sound=sounds.bighit,
            )
            sour_spot = Hitbox(
                owner=character,
                y_offset=30,
                width=100,
                height=100,
                rotation=0,
                base_knockback=5,
                knockback_angle=290,
                knockback_growth=10,
                damage=10,
                higher_priority_sibling=sweet_spot,
            )
            self.hitbox_mapping = {
                (1, 3): [sweet_spot],
                (4, 6): [sweet_spot, sour_spot],
                (7, 10): [sour_spot],
            }
            super().__init__(character)

        def __call__(self):
            super().__call__()
            character = self.character
            if character.animation_frame == 5:
                character.state = character.state_stand

    class UpSmash(Move):
        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                y_offset=-30,
                width=60,
                height=60,
                rotation=0,
                base_knockback=10,
                knockback_angle=90,
                knockback_growth=20,
                damage=20,
            )
            sour_spot = Hitbox(
                owner=character,
                y_offset=-30,
                width=100,
                height=100,
                rotation=0,
                base_knockback=5,
                knockback_angle=90,
                knockback_growth=10,
                damage=10,
                higher_priority_sibling=sweet_spot,
            )
            self.hitbox_mapping = {
                (1, 3): [sweet_spot],
                (4, 6): [sweet_spot, sour_spot],
                (7, 10): [sour_spot],
            }
            super().__init__(character)

        def __call__(self):
            super().__call__()
            character = self.character
            if character.animation_frame == 5:
                character.state = character.state_stand

    class ForwardSmash(Move):
        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                x_offset=30,
                width=60,
                height=60,
                rotation=45,
                base_knockback=10,
                knockback_angle=30,
                knockback_growth=20,
                damage=20,
                sound=sounds.sword_hit,
            )
            sour_spot = Hitbox(
                owner=character,
                x_offset=30,
                width=100,
                height=100,
                rotation=0,
                base_knockback=5,
                knockback_angle=45,
                knockback_growth=10,
                damage=10,
                higher_priority_sibling=sweet_spot,
                sound=sounds.sword_hit2,
            )
            self.hitbox_mapping = {
                (1, 3): [sweet_spot],
                (4, 6): [sweet_spot, sour_spot],
                (7, 10): [sour_spot],
            }
            super().__init__(character)

        def __call__(self):
            super().__call__()
            character = self.character
            if character.animation_frame == 5:
                character.state = character.state_stand

    class DashAttack(Move):
        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                x_offset=30,
                width=30,
                height=30,
                rotation=45,
                base_knockback=70,
                knockback_angle=80,
                # knockback_growth=20,
                damage=20,
                sound=sounds.sword_hit,
            )
            sour_spot = Hitbox(
                owner=character,
                x_offset=30,
                width=20,
                height=20,
                rotation=0,
                base_knockback=30,
                knockback_angle=45,
                # knockback_growth=10,
                damage=10,
                higher_priority_sibling=sweet_spot,
                sound=sounds.sword_hit2,
            )
            self.hitbox_mapping = {
                (1, 3): [sweet_spot],
                (4, 6): [sweet_spot, sour_spot],
                (7, 10): [sour_spot],
            }
            super().__init__(character)

        def __call__(self):
            super().__call__()
            character = self.character
            if character.animation_frame == 10:
                character.state = character.state_stand


    class DownTilt(Move):
        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                x_offset=30,
                y_offset=30,
                width=20,
                height=20,
                rotation=0,
                base_knockback=10,
                knockback_angle=-10,
                knockback_growth=8,
                damage=20,
            )
            sour_spot = Hitbox(
                owner=character,
                x_offset=10,
                y_offset=30,
                width=30,
                height=30,
                rotation=0,
                base_knockback=5,
                knockback_angle=-10,
                knockback_growth=8,
                damage=10,
                higher_priority_sibling=sweet_spot,
            )
            self.hitbox_mapping = {
                (1, 3): [sweet_spot],
                (4, 6): [sweet_spot, sour_spot],
            }
            super().__init__(character)

        def __call__(self):
            super().__call__()
            character = self.character
            if character.animation_frame == 5:
                character.state = character.state_stand


    class ForwardTilt(Move):
        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                x_offset=30,
                y_offset=0,
                width=20,
                height=20,
                rotation=0,
                base_knockback=10,
                knockback_angle=45,
                knockback_growth=8,
                damage=20,
            )
            sour_spot = Hitbox(
                owner=character,
                x_offset=10,
                y_offset=0,
                width=30,
                height=30,
                rotation=0,
                base_knockback=5,
                knockback_angle=45,
                knockback_growth=8,
                damage=10,
                higher_priority_sibling=sweet_spot,
            )
            self.hitbox_mapping = {
                (1, 3): [sweet_spot],
                (4, 6): [sweet_spot, sour_spot],
            }
            super().__init__(character)

        def __call__(self):
            super().__call__()
            character = self.character
            if character.animation_frame == 5:
                character.state = character.state_stand

