import pygame

from base.inputs import GamecubeController
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


""" 
Merge/unify KeyHandler and this. There are a lot of similar inputs. KeyHandler is basically the 
InputHandler for the keyboard. 

Use a lookup rather than having the button/axis name in the function. Save that for the 
specific controller handler instance.

How to handle button/axis inputs for the same action? E.g. "left" mapping to a) keyboard "D" 
button, but also to the grey stick x axis on a GC controller? I want to be able to access a) the 
value of the grey stick axis (for drift in increments between 0--1) and b) I want to know if the 
player just "pressed" "left". 

Maybe for each input have a value lookup (0/1 for buttons; 0--1 for axes) and also a "pressed" 
criteria, which for both could be "is the value > 0.2". 

INPUT DEVICE    INPUT NAMES     VOLLEYBALL INPUTS
============    ===========     =================
GC controller
-------------
button 0        X               jump
button 1        A               defend
button 2        B               attack
axis 0          ANALOG_X        left/right
axis 1          ANALOG_Y        up/down

Keyboard        
pygame.key      pygame key 
.get_pressed()  names
button 0        E               up
button 1        S               left
button 2        A               attack
button 4        Z               defend
"""
