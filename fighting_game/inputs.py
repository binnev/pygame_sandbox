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


class SingleInput:
    def __init__(self, id: int, parent=None):
        """
        Class to describe a single input channel on a joystick/controller -- e.g. the "A" button
        on a gamecube controller. Implements methods which check with the parent input device
        whether this button is pressed, released, etc. This allows for the more pleasant shorthand:
        `controller.a_button.is_pressed` instead of `controller.is_pressed(controller.a_button)`

        :param int id: index of this input channel in the controller.get_values() tuple
        """
        self.id = id
        self.parent = parent

    @property
    def is_down(self):
        return self.parent.is_down(self.id)

    @property
    def is_pressed(self):
        return self.parent.is_pressed(self.id)

    @property
    def is_released(self):
        return self.parent.is_released(self.id)


class GamecubeController(GamecubeControllerInputQueue):

    # input channels in CAPITALS to differentiate them from other methods
    LEFT = SingleInput(gamecube.GREY_STICK_LEFT)
    RIGHT = SingleInput(gamecube.GREY_STICK_RIGHT)
    UP = SingleInput(gamecube.GREY_STICK_UP)
    DOWN = SingleInput(gamecube.GREY_STICK_DOWN)
    A = SingleInput(gamecube.A)
    B = SingleInput(gamecube.B)
    X = SingleInput(gamecube.X)
    Y = SingleInput(gamecube.Y)
    C_UP = SingleInput(gamecube.YELLOW_STICK_UP)
    C_DOWN = SingleInput(gamecube.YELLOW_STICK_DOWN)
    C_LEFT = SingleInput(gamecube.YELLOW_STICK_LEFT)
    C_RIGHT = SingleInput(gamecube.YELLOW_STICK_RIGHT)
    START = SingleInput(pygame.K_RETURN)
    D_PAD_UP = SingleInput(gamecube.D_PAD_UP)
    L = SingleInput(gamecube.L_AXIS)
    R = SingleInput(gamecube.R_AXIS)

    def __init__(self, controller_id: int, queue_length=5):
        controller = GamecubeControllerReader(controller_id)
        self.controller_id = controller_id
        super().__init__(controller, queue_length=queue_length)

        # for each parentless SingleInput declared on the class, create a new SingleInput
        # instance with self as parent.
        for name, attr in self.__class__.__dict__.items():
            if isinstance(attr, SingleInput):
                inp = SingleInput(attr.id, parent=self)
                setattr(self, name, inp)


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
