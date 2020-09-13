import time

import pygame

from base import draw
from base.draw import Canvas
from base.game import Game
from base.inputs.keyboard import KeyboardInputQueue
from volleyball_game import conf

from volleyball_game.inputs import GamecubeController, Keyboard1, Keyboard0
from volleyball_game.levels import VolleyballCourt
from volleyball_game.objects import Stickman, Volleyball, Bowlingball, ParticleEffect


class VolleyballGame(Game):
    fps = conf.FPS
    window_width = conf.SCREEN_WIDTH
    window_height = conf.SCREEN_HEIGHT
    window_caption = "LAG SPIKE"
    ticks_per_frame = conf.TICKS_PER_SPRITE_FRAME

    def __init__(self):
        super().__init__()
        self.font = pygame.font.Font(pygame.font.match_font("ubuntu"), 50)
        Canvas.initialise()
        self.keyboard = KeyboardInputQueue()
        self.keyboard0 = Keyboard0()
        self.keyboard1 = Keyboard1()
        self.controller0 = GamecubeController(controller_id=0)
        self.controller1 = GamecubeController(controller_id=1)
        self.input_devices = [
            self.keyboard,
            self.keyboard0,
            self.keyboard1,
            self.controller0,
            self.controller1,
        ]

    def run(self):

        self.window.fill((255, 255, 255))
        level = VolleyballCourt(game=self)
        starting_positions = [
            (conf.SCREEN_WIDTH // 4, conf.SCREEN_HEIGHT - 100),
            (3 * conf.SCREEN_WIDTH // 4, conf.SCREEN_HEIGHT - 100),
        ]

        player1 = Stickman(*starting_positions[0], input=self.controller0, facing_right=True,)
        player2 = Stickman(*starting_positions[1], input=self.keyboard1, facing_right=False,)
        level.add(
            player1, player2, type="character",
        )

        def reset():
            player1.xy = starting_positions[0]
            player1.u = player1.v = 0
            player1.state = player1.states.STAND
            player2.xy = starting_positions[1]
            player2.u = player2.v = 0
            player2.state = player2.states.STAND

        run = True
        debug = False
        frame_by_frame = False
        ii = 0
        score = [0, 0]
        to_serve = "left"
        ball_in_play = False
        game_started = False
        while run:
            ii += 1
            for input_device in self.input_devices:
                input_device.read_new_inputs()
            self.window.fill((255, 255, 255))  # clear screen
            Canvas.get_instance().fill((255, 255, 255))

            if self.keyboard.is_pressed(pygame.K_ESCAPE):
                run = False
                time.sleep(2)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    button = pygame.mouse.get_pressed()
                    x, y = pygame.mouse.get_pos()
                    if button[0]:
                        level.add(ParticleEffect(x, y), type="particle_effect")
                    if button[-1]:
                        level.add(Volleyball(x, y), type="projectile")

            if self.keyboard.is_pressed(pygame.K_F1):
                debug = not debug
            if self.keyboard.is_pressed(pygame.K_RETURN):
                game_started = not game_started
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

            # tee up the ball for whoever's turn it is to serve
            if not ball_in_play and game_started:
                reset()
                x = player1.x if to_serve == "left" else player2.x
                level.add(Volleyball(x, 100), type="projectile")
                ball_in_play = True

            # do scoring if ball bounces off ground.
            bouncing_balls = pygame.sprite.spritecollide(
                level.ground, level.projectiles, dokill=False
            )
            for ball in bouncing_balls:
                time.sleep(1)
                # right player goal
                if ball.x < level.net.x:
                    score[-1] += 1
                    to_serve = "left"
                else:
                    score[0] += 1
                    to_serve = "right"
                ball.kill()
                ball_in_play = False

            # do scoring if ball falls off bottom
            for ball in level.projectiles:
                if ball.rect.bottom > conf.SCREEN_HEIGHT:
                    # player 1 knocked the ball out
                    if ball.last_touched_by == player1:
                        score[-1] += 1
                        to_serve = "left"
                    else:
                        score[0] += 1
                        to_serve = "right"
                    time.sleep(1)
                    ball_in_play = False
                    ball.kill()

            # do scoring if ball bounces off net
            bouncing_balls = pygame.sprite.spritecollide(level.net, level.projectiles, dokill=False)
            for ball in bouncing_balls:
                # if the ball bounces off the top of the net, ignore it
                if ball.centroid.y < level.net.rect.top:
                    continue
                if ball.last_touched_by == player1:
                    score[-1] += 1
                    to_serve = "left"
                else:
                    score[0] += 1
                    to_serve = "right"
                time.sleep(1)
                ball_in_play = False
                ball.kill()

            if score[0] == 5 or score[1] == 5:
                winner = "Left" if score[0] == 5 else "Right"
                text = self.font.render(
                    f"{winner} player wins {score[0]}-{score[1]}", True, (0, 0, 0)
                )
                textRect = text.get_rect()
                textRect.center = (self.window_width // 2, 50)
                self.window.blit(text, textRect)
                pygame.display.flip()
                time.sleep(3)
                score = [0, 0]
                reset()

            # wait for button press before advancing
            if frame_by_frame:
                if not self.keyboard.is_pressed(pygame.K_F3):
                    print(f"waiting on frame {ii}")
                    continue  # skip the rest of the actions
                else:
                    print("advanced 1 frame")

            level.update()

            # draw stuff
            level.draw(self.window, debug=debug)
            # draw scoreboard
            text = self.font.render(f"{score[0]}-{score[1]}", True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (self.window_width // 2, 50)
            self.window.blit(text, textRect)

            # Canvas draws its contents to screen once per tick.
            # Canvas.blit_to_window()
            pygame.display.flip()

            # destroy hitboxes
            level.hitboxes.kill()

            self.clock.tick(self.fps)
