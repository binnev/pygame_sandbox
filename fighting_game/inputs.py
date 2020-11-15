import pygame

from base.inputs.keyboard import KeyboardInputQueue


class FightingGameInput:
    # these are the inputs expected by this game.
    LEFT: int
    RIGHT: int
    UP: int
    DOWN: int
    A: int
    B: int
    X: int
    Y: int
    START: int


class KeyboardInput(FightingGameInput, KeyboardInputQueue):
    LEFT = pygame.K_a
    RIGHT = pygame.K_d
    UP = pygame.K_w
    DOWN = pygame.K_s
    A = pygame.K_j
    B = pygame.K_i
    X = pygame.K_o
    Y = pygame.K_SPACE
    START = pygame.K_p


# todo: maybe put the calculations for "is someone pressing down on the c stick, and not right" here