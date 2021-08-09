import pygame

from base.inputs import gamecube
from base.inputs.gamecube import GamecubeControllerInputQueue, GamecubeControllerReader
from base.inputs.keyboard import KeyboardInputQueue


class GamecubeController(GamecubeControllerInputQueue):
    """VolleyballGame objects will receive this as their `input` parameter.
    They will do stuff like:
    ```
    input = self.input  # "input" = the instance of this class
    if input.is_pressed(input.LEFT):
        # do action for left
    ```
    it's necessary to refer to input.LEFT (and not import LEFT from somewhere else) because it is
    specific to the input device. GamecubeController.LEFT will be a different value to
    Keyboard.LEFT.
    """

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
    D_PAD_UP = pygame.K_q


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
    D_PAD_UP = pygame.K_i


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
