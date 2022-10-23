import pygame
from robingame.input import KeyboardInputQueue, ButtonInput


class KeyboardPlayer(KeyboardInputQueue):
    def __init__(self):
        super().__init__()
        # for each parentless SingleInput declared on the class, create a new SingleInput
        # instance with self as parent.
        button_inputs = {
            name: attr
            for _class in self.__class__.__mro__
            for name, attr in _class.__dict__.items()
            if issubclass(_class, KeyboardPlayer) and isinstance(attr, ButtonInput)
        }
        for name, attr in button_inputs.items():
            inp = ButtonInput(attr.id, parent=self)
            setattr(self, name, inp)


class KeyboardPlayer1(KeyboardPlayer):
    slap = ButtonInput(pygame.K_d)
    dodge = ButtonInput(pygame.K_s)
    feint = ButtonInput(pygame.K_d)


class KeyboardPlayer2(KeyboardPlayer):
    slap = ButtonInput(pygame.K_j)
    dodge = ButtonInput(pygame.K_k)
    feint = ButtonInput(pygame.K_l)
