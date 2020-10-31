import sys
import time
from random import random

import pygame
from pygame import Color
from pygame.sprite import Sprite

from base.animation import ease_in_out
from base.draw import Canvas
from base.game import Game
from base.groups import EntityGroup
from base.objects.gui_elements import GuiButton
from base.objects.menu_test import Menu
from volleyball_game import conf
from volleyball_game.inputs import GamecubeController, Keyboard1, Keyboard0
from volleyball_game.levels import VolleyballCourt
from volleyball_game.objects import ParticleEffect
from volleyball_game.objects import (
    Stickman,
    Volleyball,
    HitHandler,
)


class VolleyballGame(Game):
    fps = conf.FPS
    window_width = conf.SCREEN_WIDTH
    window_height = conf.SCREEN_HEIGHT
    window_caption = "LAG SPIKE"
    frame_duration = conf.FRAME_DURATION
    font_name = "ubuntu"
    font_size = 50

    def __init__(self):
        super().__init__()
        self.canvas = Canvas.initialise()
        self.scenes = EntityGroup()

        # input devices that are specific to this game
        self.keyboard0 = Keyboard0()
        self.keyboard1 = Keyboard1()
        # self.controller0 = GamecubeController(controller_id=0)
        # self.controller1 = GamecubeController(controller_id=1)
        self.input_devices += [
            self.keyboard0,
            self.keyboard1,
            # self.controller0,
            # self.controller1,
        ]

    def add_scene(self, scene):
        scene.game = self
        self.scenes.add(scene)

    def main(self):
        """This is the outermost game function which runs once. It contains the outermost game
        loop. Here's where you should put your main event state machine."""
        self.add_scene(MainMenu())
        self.debug = False
        self.frame_by_frame = False
        self.tick = 0
        running = True
        while running:
            self.window.fill((255, 255, 255))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_F1:
                        self.debug = not self.debug
                    if event.key == pygame.K_F2:
                        self.frame_by_frame = not self.frame_by_frame

            # input devices should be read once per tick in the main game loop.
            # That can be the single source of truth regarding inputs.
            for device in self.input_devices:
                device.read_new_inputs()

            self.frame_by_frame_mode()
            self.scenes.update()
            self.scenes.draw(self.window, debug=self.debug)
            pygame.display.update()

            self.clock.tick(self.fps)
            self.tick += 1
            if not self.scenes:
                running = False

    def frame_by_frame_mode(self):
        # frame-by-frame mode
        while self.frame_by_frame:
            next_frame = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_F1:
                        self.debug = not self.debug
                    if event.key == pygame.K_F2:
                        self.frame_by_frame = not self.frame_by_frame
                    if event.key == pygame.K_F3:
                        next_frame = True
            if next_frame:
                break
            self.clock.tick(self.fps)


class VolleyballMatch(Sprite):
    """ The scene in which the volleyballmatch takes place. """

    game: VolleyballGame  # added by the game when it adds this scene
    starting_positions = [
        (conf.SCREEN_WIDTH // 4, conf.SCREEN_HEIGHT - 100),
        (3 * conf.SCREEN_WIDTH // 4, conf.SCREEN_HEIGHT - 100),
    ]

    def update(self):
        self.state()
        for group in self.groups:
            group.update()

    def draw(self, surface, debug=False):
        for group in self.groups:
            group.draw(surface, debug)

        # draw scoreboard
        text = self.game.font.render(f"{self.score[0]}-{self.score[1]}", True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (self.game.window_width // 2, 50)
        self.game.window.blit(text, textRect)

    def __init__(self):
        super().__init__()
        self.state = self.start_match
        self.level = VolleyballCourt()
        self.groups = [self.level]
        self.frame_by_frame = False
        self.hit_handler = HitHandler()
        self.score = [0, 0]
        self.to_serve = "left"
        self.ball_in_play = False
        self.game_started = False
        self.max_score = 10

    def reset_match(self):
        self.game.add_scene(VolleyballMatch())
        self.kill()

    def start_match(self):
        """Stuff that can't go in the init method (probably because it refers to self.game
        before that property has been set."""
        self.player1 = Stickman(
            *self.starting_positions[0],
            input=self.game.keyboard0,
            facing_right=True,
        )
        self.player2 = Stickman(
            *self.starting_positions[1],
            input=self.game.keyboard1,
            facing_right=False,
        )
        self.level.add(self.player1, self.player2, type="character")
        self.state = self.match

    def match(self):
        """ Main state function """
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                button = pygame.mouse.get_pressed()

        # reset
        if self.game.keyboard.is_pressed(pygame.K_BACKSPACE):
            self.reset_match()

        if self.game.keyboard.is_pressed(pygame.K_RETURN):
            self.game_started = not self.game_started

        self.tee_up()
        self.score_bouncing_balls()
        self.score_balls_out_of_play()
        self.end_game()

        self.hit_handler.handle_hits(
            self.level.hitboxes, [*self.level.characters, *self.level.projectiles]
        )

        # destroy hitboxes
        self.level.hitboxes.kill()

    def reset_player_positions(self):
        self.player1.xy = self.starting_positions[0]
        self.player1.u = self.player1.v = 0
        self.player1.facing_right = True
        self.player1.state = self.player1.state_stand
        self.player2.xy = self.starting_positions[1]
        self.player2.u = self.player2.v = 0
        self.player2.facing_right = False
        self.player2.state = self.player2.state_stand

    def score_bouncing_balls(self):
        """ do scoring if ball bounces off ground. """
        bouncing_balls = pygame.sprite.spritecollide(
            self.level.ground, self.level.projectiles, dokill=False
        )
        for ball in bouncing_balls:
            time.sleep(1)
            # right player goal
            if ball.x < self.level.net.x:
                self.score[-1] += 1
                self.to_serve = "left"
            else:
                self.score[0] += 1
                self.to_serve = "right"
            ball.kill()
            self.ball_in_play = False

    def tee_up(self):
        # # tee up the ball for whoever's turn it is to serve
        if not self.ball_in_play and self.game_started:
            self.reset_player_positions()
            x = self.player1.x if self.to_serve == "left" else self.player2.x
            self.level.add(Volleyball(x, 100), type="projectile")
            self.ball_in_play = True

    def score_balls_out_of_play(self):
        # do scoring if ball falls off bottom
        for ball in self.level.projectiles:
            if ball.rect.bottom > conf.SCREEN_HEIGHT:
                # player 1 knocked the ball out
                if ball.last_touched_by == self.player1:
                    self.score[-1] += 1
                    self.to_serve = "left"
                else:
                    self.score[0] += 1
                    self.to_serve = "right"
                time.sleep(1)
                self.ball_in_play = False
                ball.kill()

    def score_balls_in_net(self):
        # do scoring if ball bounces off net
        bouncing_balls = pygame.sprite.spritecollide(
            self.level.net, self.level.projectiles, dokill=False
        )
        for ball in bouncing_balls:
            # if the ball bounces off the top of the net, ignore it
            if ball.centroid.y < self.level.net.rect.top:
                continue
            if ball.last_touched_by == self.player1:
                self.score[-1] += 1
                self.to_serve = "left"
            else:
                self.score[0] += 1
                self.to_serve = "right"
            time.sleep(1)
            self.ball_in_play = False
            ball.kill()

    def end_game(self):
        # end the game
        if self.score[0] == self.max_score or self.score[1] == self.max_score:
            winner = "Left" if self.score[0] == self.max_score else "Right"
            text = self.game.font.render(
                f"{winner} player wins {self.score[0]}-{self.score[1]}", True, (0, 0, 0)
            )
            textRect = text.get_rect()
            textRect.center = (self.game.window_width // 2, 50)
            self.game.window.blit(text, textRect)
            pygame.display.flip()
            time.sleep(3)
            self.score = [0, 0]
            self.reset_player_positions()


class MainMenu(Menu):
    animation_time = 40

    def __init__(self):
        super().__init__()
        self.state = self.animate_in
        self.play_button = GuiButton(
            -999,
            200,
            200,
            50,
            text="PLAY!",
            text_color=Color("white"),
            color=(100, 0, 100),
        )
        self.quit_button = GuiButton(
            -999,
            400,
            200,
            50,
            text="quit",
            text_color=Color("white"),
            color=(100, 0, 100),
        )
        self.settings_button = GuiButton(
            -999,
            300,
            200,
            50,
            text="settings",
            text_color=Color("white"),
            color=(100, 0, 100),
        )
        self.buttons.add(self.play_button, self.quit_button, self.settings_button)
        self.explosions = EntityGroup()
        self.groups.append(self.explosions)

    def animate_in(self):
        try:
            # todo: maybe make these generators so that you're not generating the entire array
            #  each tick
            xs = ease_in_out(-250, conf.SCREEN_WIDTH // 2, self.animation_time)
            for button in self.buttons:
                button.x = xs[self.game_tick]
        except IndexError:
            self.state = self.idle

    def idle(self):
        if self.quit_button.click:
            self.state = self.animate_to(self.animate_out, None)
        if self.settings_button.click:
            self.game.add_scene(SettingsMenu())
            self.state = self.animate_to(self.animate_out, None)
        if self.play_button.click:
            self.game.add_scene(VolleyballMatch())
            self.state = self.animate_to(self.animate_out, None)

            for ii in range(30):
                self.explosions.add(
                    ParticleEffect(x=random() * conf.SCREEN_WIDTH, y=random() * conf.SCREEN_HEIGHT)
                ),

    def animate_out(self, next_scene):
        try:
            xs = ease_in_out(conf.SCREEN_WIDTH // 2, conf.SCREEN_WIDTH + 250, self.animation_time)
            for button in self.buttons:
                button.x = xs[self.game_tick]
        except IndexError:
            if next_scene:
                self.game.scenes.add(next_scene)
            self.kill()


class SettingsMenu(Menu):
    animation_time = 40

    def __init__(self):
        super().__init__()
        self.state = self.animate_in
        self.back_button = GuiButton(
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
            xs = ease_in_out(-250, conf.SCREEN_WIDTH // 2, self.animation_time)
            self.back_button.x = xs[self.game_tick]
        except IndexError:
            self.state = self.idle

    def idle(self):
        if self.back_button.click:
            self.game.add_scene(MainMenu())
            self.state = self.animate_to(self.animate_out, None)

    def animate_out(self, next_scene):
        try:
            xs = ease_in_out(conf.SCREEN_WIDTH // 2, conf.SCREEN_WIDTH + 250, self.animation_time)
            self.back_button.x = xs[self.game_tick]
        except IndexError:
            if next_scene:
                self.game.scenes.add(next_scene)
            self.kill()
