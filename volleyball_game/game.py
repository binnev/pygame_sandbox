import time

import pygame

from base import draw
from base.draw import Canvas
from base.game import Game
from base.inputs.keyboard import KeyboardInputQueue
from volleyball_game import conf
from volleyball_game.inputs import GamecubeController, Keyboard1, Keyboard0
from volleyball_game.levels import VolleyballCourt
from volleyball_game.objects import (
    Stickman,
    Volleyball,
    HitHandler,
    PersistentHitbox,
)


class VolleyballGame(Game):
    fps = conf.FPS
    window_width = conf.SCREEN_WIDTH
    window_height = conf.SCREEN_HEIGHT
    window_caption = "LAG SPIKE"
    ticks_per_frame = conf.TICKS_PER_SPRITE_FRAME
    font_name = "ubuntu"
    font_size = 50

    def __init__(self):
        super().__init__()
        self.canvas = Canvas.initialise()

        # input devices that are specific to this game
        self.keyboard0 = Keyboard0()
        self.keyboard1 = Keyboard1()
        self.controller0 = GamecubeController(controller_id=0)
        self.controller1 = GamecubeController(controller_id=1)
        self.input_devices += [
            self.keyboard0,
            self.keyboard1,
            self.controller0,
            self.controller1,
        ]

    def run(self):

        # setup stuff before the main game loop:
        self.window.fill((255, 255, 255))
        level = VolleyballCourt(game=self)
        starting_positions = [
            (conf.SCREEN_WIDTH // 4, conf.SCREEN_HEIGHT - 100),
            (3 * conf.SCREEN_WIDTH // 4, conf.SCREEN_HEIGHT - 100),
        ]

        player1 = Stickman(*starting_positions[0], input=self.controller0, facing_right=True,)
        player2 = Stickman(*starting_positions[1], input=self.controller1, facing_right=False,)
        level.add(
            player1, player2, type="character",
        )
        hit_handler = HitHandler()

        def reset():
            player1.xy = starting_positions[0]
            player1.u = player1.v = 0
            player1.state = player1.state_stand
            player2.xy = starting_positions[1]
            player2.u = player2.v = 0
            player2.state = player2.state_stand

        def score_bouncing_balls(level, match):
            """ do scoring if ball bounces off ground. """
            bouncing_balls = pygame.sprite.spritecollide(
                level.ground, level.projectiles, dokill=False
            )
            for ball in bouncing_balls:
                time.sleep(1)
                # right player goal
                if ball.x < level.net.x:
                    match.score[-1] += 1
                    match.to_serve = "left"
                else:
                    match.score[0] += 1
                    match.to_serve = "right"
                ball.kill()
                match.ball_in_play = False

        def tee_up(level, match, player1, player2):
            # tee up the ball for whoever's turn it is to serve
            reset()
            x = player1.x if match.to_serve == "left" else player2.x
            level.add(Volleyball(x, 100), type="projectile")
            match.ball_in_play = True

        def score_balls_out_of_play(level, match):
            # do scoring if ball falls off bottom
            for ball in level.projectiles:
                if ball.rect.bottom > conf.SCREEN_HEIGHT:
                    # player 1 knocked the ball out
                    if ball.last_touched_by == player1:
                        match.score[-1] += 1
                        match.to_serve = "left"
                    else:
                        match.score[0] += 1
                        match.to_serve = "right"
                    time.sleep(1)
                    match.ball_in_play = False
                    ball.kill()

        def score_balls_in_net(level, match):
            # do scoring if ball bounces off net
            bouncing_balls = pygame.sprite.spritecollide(level.net, level.projectiles, dokill=False)
            for ball in bouncing_balls:
                # if the ball bounces off the top of the net, ignore it
                if ball.centroid.y < level.net.rect.top:
                    continue
                if ball.last_touched_by == player1:
                    match.score[-1] += 1
                    match.to_serve = "left"
                else:
                    match.score[0] += 1
                    match.to_serve = "right"
                time.sleep(1)
                match.ball_in_play = False
                ball.kill()

        def end_game(level, match):
            # end the game
            if match.score[0] == match.max_score or match.score[1] == match.max_score:
                winner = "Left" if match.score[0] == match.max_score else "Right"
                text = self.font.render(
                    f"{winner} player wins {match.score[0]}-{match.score[1]}", True, (0, 0, 0)
                )
                textRect = text.get_rect()
                textRect.center = (self.window_width // 2, 50)
                self.window.blit(text, textRect)
                pygame.display.flip()
                time.sleep(3)
                match.score = [0, 0]
                reset()

        run = True
        debug = False
        frame_by_frame = False

        # fixme: this is ugly and hacky
        class Match:
            score = [0, 0]
            to_serve = "left"
            ball_in_play = False
            game_started = False
            max_score = 10

        # main volleyball game loop:
        while run:
            # todo: duplicated
            for device in self.input_devices:
                device.read_new_inputs()
            self.window.fill((255, 255, 255))  # clear screen
            Canvas.get_instance().fill((255, 255, 255))

            if self.keyboard.is_pressed(pygame.K_ESCAPE):
                run = False
                time.sleep(1)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    button = pygame.mouse.get_pressed()
                    x, y = pygame.mouse.get_pos()
                    if button[0]:
                        level.add(PersistentHitbox(x, y), type="particle_effect")
                    # if button[-1]:
                    #     level.add(Bowlingball(x, y), type="projectile")

            if self.keyboard.is_pressed(pygame.K_F1):
                debug = not debug
            if self.keyboard.is_pressed(pygame.K_RETURN):
                Match.game_started = not Match.game_started
            if self.keyboard.is_pressed(pygame.K_F2):
                frame_by_frame = not frame_by_frame
            if self.keyboard.is_pressed(pygame.K_b):
                level.add(
                    Volleyball(conf.SCREEN_WIDTH // 4, conf.SCREEN_HEIGHT // 4), type="projectile"
                )
            if self.keyboard.is_down(pygame.K_r):
                transparent_red = (*pygame.color.THECOLORS["red"][:3], 150)
                draw.rect(self.window, transparent_red, (200, 100, 60, 200))
                # we draw to canvas using standard pygame drawing methods
                pygame.draw.rect(Canvas.get_instance(), transparent_red, (100, 100, 60, 200))

            if not Match.ball_in_play and Match.game_started:
                tee_up(level, Match, player1, player2)
            score_bouncing_balls(level, Match)
            score_balls_out_of_play(level, Match)
            score_balls_in_net(level, Match)
            end_game(level, Match)

            # wait for button press before advancing
            if frame_by_frame:
                if not self.keyboard.is_pressed(pygame.K_F3):
                    continue  # skip the rest of the actions
                else:
                    print("advanced 1 frame")

            level.update()
            hit_handler.handle_hits(level.hitboxes, [*level.characters, *level.projectiles])

            # draw stuff
            level.draw(self.window, debug=debug)
            # draw scoreboard
            text = self.font.render(f"{Match.score[0]}-{Match.score[1]}", True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (self.window_width // 2, 50)
            self.window.blit(text, textRect)

            # Canvas draws its contents to screen once per tick.
            # Canvas.blit_to_window()
            pygame.display.flip()

            # destroy hitboxes
            level.hitboxes.kill()

            self.clock.tick(self.fps)
