import pygame

from base.inputs import gamecube
from base.inputs.gamecube import GamecubeControllerReader, GamecubeControllerInputQueue
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
    L: int
    R: int


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
    L = pygame.K_ESCAPE
    R = pygame.K_ESCAPE


class GamecubeController(GamecubeControllerInputQueue):
    # todo: rethink this. This class should be deciding if a button was just pressed (or if a
    #  user drops through a platform or crouches on the platform). Not the reader class.

    # key mapping
    LEFT = gamecube.GREY_STICK_LEFT
    RIGHT = gamecube.GREY_STICK_RIGHT
    UP = gamecube.GREY_STICK_UP
    DOWN = gamecube.GREY_STICK_DOWN
    A = gamecube.A
    B = gamecube.B
    X = gamecube.X
    Y = gamecube.Y
    C_UP = gamecube.YELLOW_STICK_UP
    C_DOWN = gamecube.YELLOW_STICK_DOWN
    C_LEFT = gamecube.YELLOW_STICK_LEFT
    C_RIGHT = gamecube.YELLOW_STICK_RIGHT
    START = pygame.K_RETURN
    D_PAD_UP = gamecube.D_PAD_UP
    L = gamecube.L_AXIS
    R = gamecube.R_AXIS

    def __init__(self, controller_id, queue_length=5):
        controller = GamecubeControllerReader(controller_id)
        super().__init__(controller, queue_length=queue_length)


class Keyboard0(KeyboardInputQueue):
    LEFT = pygame.K_s
    RIGHT = pygame.K_f
    UP = None
    DOWN = pygame.K_d
    A = pygame.K_z
    B = pygame.K_a
    X = None
    Y = pygame.K_e
    C_UP = pygame.K_ESCAPE  # fixme
    C_DOWN = pygame.K_ESCAPE  # fixme
    C_LEFT = pygame.K_ESCAPE  # fixme
    C_RIGHT = pygame.K_ESCAPE  # fixme
    START = pygame.K_RETURN
    D_PAD_UP = pygame.K_ESCAPE  # fixme
    L = pygame.K_ESCAPE  # fixme
    R = pygame.K_ESCAPE  # fixme


class Keyboard1(Keyboard0):
    LEFT = pygame.K_l
    RIGHT = pygame.K_QUOTE
    UP = None
    DOWN = pygame.K_SEMICOLON
    A = pygame.K_COMMA
    B = pygame.K_k
    X = None
    Y = pygame.K_p
    C_UP = pygame.K_ESCAPE  # fixme
    C_DOWN = pygame.K_ESCAPE  # fixme
    C_LEFT = pygame.K_ESCAPE  # fixme
    C_RIGHT = pygame.K_ESCAPE  # fixme
    START = pygame.K_RETURN
    D_PAD_UP = pygame.K_ESCAPE  # fixme
    L = pygame.K_ESCAPE  # fixme
    R = pygame.K_ESCAPE  # fixme


# todo: maybe put the calculations for "is someone pressing down on the c stick, and not right" here
