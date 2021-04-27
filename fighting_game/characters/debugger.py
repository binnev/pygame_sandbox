from copy import copy

import pygame
from pygame import Color, Surface

from fighting_game import sounds
from fighting_game.characters import Character, AerialMove, Move
from fighting_game.hitboxes import Hitbox
from fighting_game.inputs import FightingGameInput
from fighting_game.projectiles.falco_laser import FalcoLaser
from fighting_game.sprites.stickman import stickman_sprites


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
            f"hitstun_duration: {self.hitstun_duration}",
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
            sprite = character.sprites[f"flying_kick_{character.facing}"]
            images = sprite.frames
            image_windup = images[0]
            image_hit = images[2]
            image_endlag = images[6]

            self.frame_mapping = [
                {"image": image_windup},
                {"image": image_hit, "hitboxes": [sweet_spot]},
                {"image": image_hit, "hitboxes": [sweet_spot]},
                {"image": image_hit, "hitboxes": [sour_spot]},
                {"image": image_hit, "hitboxes": [sour_spot]},
                {"image": image_endlag},
            ]
            super().__init__(character)

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
            sprite = character.sprites[f"back_air2_{character.facing}"]
            images = sprite.frames
            image_windup = images[0]
            image_windup2 = images[1]
            image_hit = images[2]
            image_hit2 = images[3]
            image_endlag = images[4]

            self.frame_mapping = [
                {"image": image_windup},
                {"image": image_windup2},
                {"image": image_hit, "hitboxes": [sweet_spot]},
                {"image": image_hit2, "hitboxes": [sour_spot]},
                {"image": image_hit2, "hitboxes": [sour_spot]},
                {"image": image_endlag},
            ]
            super().__init__(character)

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
            sprite = character.sprites[f"aerial_defense_{character.facing}"]
            images = sprite.frames
            image_hit = images[0]
            image_endlag = images[1]
            image_endlag2 = images[2]

            self.frame_mapping = [
                {"image": image_hit, "hitboxes": [sweet_spot]},
                {"image": image_endlag, "hitboxes": [sour_spot]},
                {"image": image_endlag, "hitboxes": [sour_spot]},
                {"image": image_endlag2},
            ]
            super().__init__(character)

    class DownAir(AerialMove):
        landing_lag = 10

        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                y_offset=30,
                width=40,
                height=40,
                rotation=0,
                base_knockback=10,
                knockback_angle=280,
                knockback_growth=20,
                damage=20,
                sound=sounds.bighit,
            )
            sour_spot = Hitbox(
                owner=character,
                y_offset=0,
                width=60,
                height=60,
                rotation=0,
                base_knockback=5,
                knockback_angle=280,
                knockback_growth=10,
                damage=10,
                higher_priority_sibling=sweet_spot,
            )
            sprite = character.sprites[f"stomp_{character.facing}"]
            images = sprite.frames
            image_windup = images[1]
            image_hit = images[3]
            image_endlag = images[5]

            self.frame_mapping = [
                {"image": image_windup},
                {"image": image_windup},
                {"image": image_windup},
                {"image": image_hit},
                {"image": image_hit, "hitboxes": [sweet_spot]},
                {"image": image_hit, "hitboxes": [sweet_spot, sour_spot]},
                {"image": image_hit, "hitboxes": [sweet_spot, sour_spot]},
                {"image": image_hit, "hitboxes": [sour_spot]},
                {"image": image_endlag},
                {"image": image_endlag},
            ]
            super().__init__(character)

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
            sprite = character.sprites[f"stomp_{character.facing}"]
            images = sprite.frames
            image = images[1]
            sprite2 = character.sprites[f"back_air2_{character.facing}"]
            image_hit2 = sprite2.frames[3]

            self.frame_mapping = [
                {"image": image_hit2, "hitboxes": [initial_hit]},
                {"image": image},
                {"image": image},
                {"image": image_hit2, "hitboxes": [second_hit]},
                {"image": image},
                {"image": image},
                {"image": image_hit2, "hitboxes": [final_hit]},
                {"image": image},
                {"image": image},
            ]
            super().__init__(character)

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
            sprite = character.sprites[f"weird_hit_{character.facing}"]
            images = sprite.frames
            image_windup = images[1]
            image_hit = images[3]
            image_endlag = images[4]

            self.frame_mapping = [
                {"image": image_windup},
                {"image": image_hit, "hitboxes": [sweet_spot]},
                {"image": image_endlag},
                {"image": image_endlag},
                {"image": image_endlag},
            ]
            super().__init__(character)

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
            sprite = character.sprites[f"weird_hit_{character.facing}"]
            images = sprite.frames
            image_hit = images[1]

            self.frame_mapping = [
                {"image": image_hit, "hitboxes": [sweet_spot]},
                {"image": image_hit},
                {"image": image_hit},
            ]
            super().__init__(character)

    class DownSmash(Move):
        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                y_offset=30,
                width=100,
                height=100,
                rotation=0,
                base_knockback=10,
                knockback_angle=295,
                knockback_growth=20,
                damage=10,
                sound=sounds.bighit,
            )
            sour_spot = Hitbox(
                owner=character,
                y_offset=30,
                width=60,
                height=60,
                rotation=0,
                base_knockback=25,
                knockback_angle=280,
                damage=5,
            )
            sour_spot2 = copy(sour_spot)
            sour_spot3 = copy(sour_spot)
            sprite = character.sprites[f"dive_getup_{character.facing}"]
            images = sprite.frames
            image_hit = images[3]
            image_hit2 = images[5]
            image_getup1 = images[6]
            image_getup2 = images[7]
            image_getup3 = images[8]
            image_getup4 = images[9]

            self.frame_mapping = [
                {"image": image_getup4},
                {"image": image_hit, "hitboxes": [sour_spot]},
                {"image": image_hit2},
                {"image": image_hit2},
                {"image": image_hit, "hitboxes": [sour_spot2]},
                {"image": image_hit2},
                {"image": image_hit2},
                {"image": image_hit, "hitboxes": [sour_spot3]},
                {"image": image_hit2},
                {"image": image_hit2},
                {"image": image_hit, "hitboxes": [sweet_spot]},
                {"image": image_hit2},
                {"image": image_hit2},
                {"image": image_getup1},
                {"image": image_getup2},
                {"image": image_getup3},
                {"image": image_getup4},
            ]

            super().__init__(character)

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
            sprite = character.sprites[f"taunt_{character.facing}"]
            images = sprite.frames
            image_windup = images[1]
            image_windup2 = images[2]
            image_hit = images[3]
            image_hit2 = images[4]

            self.frame_mapping = [
                {"image": image_windup},
                {"image": image_windup2},
                {"image": image_hit, "hitboxes": [sour_spot]},
                {"image": image_hit2, "hitboxes": [sweet_spot]},
                {"image": image_hit},
                {"image": image_windup2},
                {"image": image_windup},
            ]
            super().__init__(character)

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
            sprite = character.sprites[f"standing_hit_{character.facing}"]
            images = sprite.frames
            image_hit = images[0]

            self.frame_mapping = [
                {"image": image_hit, "hitboxes": [sweet_spot]},
                {"image": image_hit, "hitboxes": [sour_spot]},
                {"image": image_hit},
                {"image": image_hit},
                {"image": image_hit},
                {"image": image_hit},
                {"image": image_hit},
                {"image": image_hit},
                {"image": image_hit},
                {"image": image_hit},
                {"image": image_hit},
                {"image": image_hit},
            ]
            super().__init__(character)

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
                knockback_growth=0,
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
                knockback_growth=0,
                damage=10,
                higher_priority_sibling=sweet_spot,
                sound=sounds.sword_hit2,
            )
            sprite = character.sprites[f"flying_kick_{character.facing}"]
            images = sprite.frames
            image_hit = images[1]

            self.frame_mapping = [
                {"image": image_hit, "hitboxes": [sweet_spot]},
                {"image": image_hit, "hitboxes": [sour_spot]},
                {"image": image_hit},
                {"image": image_hit},
                {"image": image_hit},
                {"image": image_hit},
            ]
            super().__init__(character)

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
            sprite = character.sprites[f"dive_getup_{character.facing}"]
            images = sprite.frames
            image_hit = images[6]

            self.frame_mapping = [
                {"image": image_hit, "hitboxes": [sweet_spot, sour_spot]},
                {"image": image_hit, "hitboxes": [sweet_spot, sour_spot]},
                {"image": image_hit},
                {"image": image_hit},
            ]
            super().__init__(character)

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
            sprite = character.sprites[f"run_{character.facing}"]
            images = sprite.frames
            image_hit = images[1]

            self.frame_mapping = [
                {"image": image_hit, "hitboxes": [sweet_spot, sour_spot]},
                {"image": image_hit, "hitboxes": [sweet_spot, sour_spot]},
                {"image": image_hit},
                {"image": image_hit},
            ]
            super().__init__(character)

    class AerialNeutralB(AerialMove):
        landing_lag = 0

        def __init__(self, character: Character):
            sprite = character.sprites[f"run_{character.facing}"]
            images = sprite.frames
            image_hit = images[1]

            self.frame_mapping = [
                {"image": image_hit},
                {"image": image_hit},
                {"image": image_hit},
                {"image": image_hit},
            ]
            character.level.add_projectile(
                FalcoLaser(
                    x=character.x,
                    y=character.y,
                    facing_right=character.facing_right,
                    owner=character,
                )
            )
            super().__init__(character)

    class AerialUpB(AerialMove):
        landing_lag = 0

        def __init__(self, character: Character):
            sweet_spot = Hitbox(
                owner=character,
                x_offset=30,
                width=50,
                height=30,
                rotation=45,
                base_knockback=50,
                knockback_angle=10,
                knockback_growth=20,
                damage=15,
                sound=sounds.sword_hit,
            )
            sour_spot = Hitbox(
                owner=character,
                x_offset=10,
                y_offset=-30,
                width=40,
                height=80,
                rotation=0,
                base_knockback=30,
                knockback_angle=45,
                knockback_growth=5,
                damage=5,
                higher_priority_sibling=sweet_spot,
                sound=sounds.sword_hit2,
            )
            sprite = character.sprites[f"back_air_{character.facing}"]
            images = sprite.frames
            image = images[2]
            image2 = character.sprites[f"crouch_{character.facing}"].frames[0]

            self.frame_mapping = [
                {"image": image2},
                {"image": image2},
                {"image": image, "hitboxes": [sweet_spot]},
                {"image": image, "hitboxes": [sweet_spot]},
                {"image": image, "hitboxes": [sour_spot]},
                {"image": image, "hitboxes": [sour_spot]},
                {"image": image, "hitboxes": [sour_spot]},
                {"image": image, "hitboxes": [sour_spot]},
                {"image": image, "hitboxes": [sour_spot]},
                {"image": image},
                {"image": image},
                {"image": image},
                {"image": image},
                {"image": image},
                {"image": image},
            ]
            character.v = -13
            character.u += 5 if character.facing_right else -5
            super().__init__(character)

        def get_next_state(self):
            return self.character.state_special_fall
