import pygame

from base.controllers import GamecubeController
from base.keyhandler import KeyHandler


class Player1:
    LEFT = pygame.K_s
    RIGHT = pygame.K_f
    UP = pygame.K_e
    DOWN = pygame.K_d
    DEFEND = pygame.K_z
    ATTACK = pygame.K_a


class Player2:
    LEFT = pygame.K_l
    RIGHT = pygame.K_QUOTE
    UP = pygame.K_p
    DOWN = pygame.K_SEMICOLON
    DEFEND = pygame.K_COMMA
    ATTACK = pygame.K_k


class KeyInputHandler:
    """ Maps certain keys to the inputs expected by the volleyball game -- e.g. 'K' maps to
    'left' input. """

    # todo: at the moment this just maps which keys are down. Make a way to record if keys have
    #  just been pressed. Maybe subclass Key_handler?

    def __init__(self, key_mapping):
        self.key_mapping = key_mapping

    @property
    def left(self):
        return KeyHandler.is_down(self.key_mapping.LEFT)

    @property
    def right(self):
        return KeyHandler.is_down(self.key_mapping.RIGHT)

    @property
    def up(self):
        return KeyHandler.is_down(self.key_mapping.UP)

    @property
    def down(self):
        return KeyHandler.is_down(self.key_mapping.DOWN)

    @property
    def defend(self):
        return KeyHandler.is_down(self.key_mapping.DEFEND)

    @property
    def attack(self):
        return KeyHandler.is_down(self.key_mapping.ATTACK)


class GamecubeControllerInputHandler:
    def __init__(self, controller_id):
        self.controller = GamecubeController(controller_id)

    @property
    def left(self):
        return self.controller.ANALOG_X < 0 and abs(self.controller.ANALOG_X) > 0.1

    @property
    def right(self):
        return self.controller.ANALOG_X > 0 and abs(self.controller.ANALOG_X) > 0.1

    @property
    def up(self):
        # return self.controller.ANALOG_Y < 0 and abs(self.controller.ANALOG_Y) > 0.1
        return self.controller.Y

    @property
    def down(self):
        return self.controller.ANALOG_Y > 0 and abs(self.controller.ANALOG_Y) > 0.1

    @property
    def defend(self):
        return self.controller.A

    @property
    def attack(self):
        return self.controller.B
