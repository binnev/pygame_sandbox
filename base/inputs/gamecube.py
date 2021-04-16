"""
# similar to pygame.key.get_pressed()
Usage:
```
controller1 = GamecubeController(1)
inputs = controller1.get_values()
if inputs[gamecube.A]:
    # do action for A
```
"""
import pygame

# button/input indices. These are used for lookup similarly to e.g. pygame.K_ESCAPE
from base.inputs.queue import InputQueue

A = 0
B = 1
X = 2
Y = 3
Z = 4
L = 5
R = 6
START = 7
GREY_STICK_LEFT = 8
GREY_STICK_RIGHT = 9
GREY_STICK_UP = 10
GREY_STICK_DOWN = 11
YELLOW_STICK_LEFT = 12
YELLOW_STICK_RIGHT = 13
YELLOW_STICK_UP = 14
YELLOW_STICK_DOWN = 15
R_AXIS = 16
L_AXIS = 17
D_PAD_LEFT = 18
D_PAD_RIGHT = 19
D_PAD_UP = 20
D_PAD_DOWN = 21


def linear_map(input_value, input_range, output_range, limit_output=True):
    """ Linearly map a set of inputs to a set of outputs. If limit_output==True, don't output any
    values outside the output range. Will still allow inputs outside the input range. """
    input_min, input_max = input_range
    output_min, output_max = output_range

    di = input_max - input_min
    do = output_max - output_min
    gradient = do / di
    offset = output_min - gradient * input_min

    # y = mx + c
    output_value = gradient * input_value + offset

    if limit_output:
        output_value = max(output_value, output_min)
        output_value = min(output_value, output_max)

    return output_value


def create_mapping(input_range, output_range, limit_output=True):
    """ Partially execute the linear_map function to store the input/output ranges so we don't
    have to input them every time. """

    def wrapper(input_value):
        return linear_map(input_value, input_range, output_range, limit_output)

    return wrapper


class GamecubeControllerReader:
    """ Class to read the inputs of a GameCube controller plugged into the Mayflash "GameCube
    Controller Adapter for Wii U & PC USB"

    This class
    - reads the values from the controller's buttons (binary values) axes (analog inputs such as
    control sticks and triggers) and hats (the 4-way D pad)
    - maps the values of the inputs to a 0-1 range and exposes these as named properties if the
    user wants to access a single value.
    - exposes a .get_values() method which returns a tuple of all the inputs (similar to how
    pygame deals with keyboard and mouse input.
    """

    # input ranges. Use these to set minimum (i.e. dead zone) and maximum input values
    GREY_STICK_INPUT_RANGE = (0.1, 0.86)
    YELLOW_STICK_INPUT_RANGE = (0.1, 0.86)
    TRIGGER_INPUT_RANGE = (-0.5, 1)

    def __init__(self, joystick_id: int):
        self.joystick = pygame.joystick.Joystick(joystick_id)  # get the joystick from pygame
        self.joystick.init()  # turn on the joystick

    def get_values(self):
        """ Get the current state of all the inputs. This is intended to be equivalent to
        pygame.key.get_pressed so that the inputs can be processed in the same way. """
        # todo: the d-pad properties each access the d-pad values when they are called. So we're
        #  checking the status of the d-pad 4 times per tick when once would do. If the inputs
        #  ever get slow, maybe look at this.
        return (
            self.A,
            self.B,
            self.X,
            self.Y,
            self.Z,
            self.L,
            self.R,
            self.START,
            self.GREY_STICK_LEFT,
            self.GREY_STICK_RIGHT,
            self.GREY_STICK_UP,
            self.GREY_STICK_DOWN,
            self.YELLOW_STICK_LEFT,
            self.YELLOW_STICK_RIGHT,
            self.YELLOW_STICK_UP,
            self.YELLOW_STICK_DOWN,
            self.R_AXIS,
            self.L_AXIS,
            self.D_PAD_LEFT,
            self.D_PAD_RIGHT,
            self.D_PAD_UP,
            self.D_PAD_DOWN,
        )

    # =================== AXES (=ANALOG INPUTS) =======================

    # uncalibrated internal values

    @property
    def _GREY_STICK_X_AXIS(self):
        return self.joystick.get_axis(0)

    @property
    def _GREY_STICK_Y_AXIS(self):
        return self.joystick.get_axis(1)

    @property
    def _YELLOW_STICK_X_AXIS(self):
        return self.joystick.get_axis(5)

    @property
    def _YELLOW_STICK_Y_AXIS(self):
        return self.joystick.get_axis(2)

    @property
    def _L_TRIGGER_AXIS(self):
        return self.joystick.get_axis(3)

    @property
    def _R_TRIGGER_AXIS(self):
        return self.joystick.get_axis(4)

    # calibrated external values

    @property
    def GREY_STICK_LEFT(self):
        return linear_map(-self._GREY_STICK_X_AXIS, self.GREY_STICK_INPUT_RANGE, (0, 1))

    @property
    def GREY_STICK_RIGHT(self):
        return linear_map(self._GREY_STICK_X_AXIS, self.GREY_STICK_INPUT_RANGE, (0, 1))

    @property
    def GREY_STICK_UP(self):
        return linear_map(-self._GREY_STICK_Y_AXIS, self.GREY_STICK_INPUT_RANGE, (0, 1))

    @property
    def GREY_STICK_DOWN(self):
        return linear_map(self._GREY_STICK_Y_AXIS, self.GREY_STICK_INPUT_RANGE, (0, 1))

    @property
    def YELLOW_STICK_LEFT(self):
        return linear_map(-self._YELLOW_STICK_X_AXIS, self.YELLOW_STICK_INPUT_RANGE, (0, 1))

    @property
    def YELLOW_STICK_RIGHT(self):
        return linear_map(self._YELLOW_STICK_X_AXIS, self.YELLOW_STICK_INPUT_RANGE, (0, 1))

    @property
    def YELLOW_STICK_UP(self):
        return linear_map(-self._YELLOW_STICK_Y_AXIS, self.YELLOW_STICK_INPUT_RANGE, (0, 1))

    @property
    def YELLOW_STICK_DOWN(self):
        return linear_map(self._YELLOW_STICK_Y_AXIS, self.YELLOW_STICK_INPUT_RANGE, (0, 1))

    @property
    def R_AXIS(self):
        return linear_map(self._R_TRIGGER_AXIS, self.TRIGGER_INPUT_RANGE, (0, 1))

    @property
    def L_AXIS(self):
        return linear_map(self._L_TRIGGER_AXIS, self.TRIGGER_INPUT_RANGE, (0, 1))

    # =================== 4-WAY SWITCHES =======================

    # uncalibrated internal values

    @property
    def _D_PAD(self):
        return self.joystick.get_hat(0)

    @property
    def _D_PAD_X(self):
        return self._D_PAD[0]

    @property
    def _D_PAD_Y(self):
        return self._D_PAD[1]

    # calibrated external values

    @property
    def D_PAD_LEFT(self):
        return int(self._D_PAD_X < 0)

    @property
    def D_PAD_RIGHT(self):
        return int(self._D_PAD_X > 0)

    @property
    def D_PAD_UP(self):
        return int(self._D_PAD_Y > 0)

    @property
    def D_PAD_DOWN(self):
        return int(self._D_PAD_Y < 0)

    # =================== BUTTONS (=BINARY VALUES) =======================

    # calibrated external values

    @property
    def X(self):
        return self.joystick.get_button(0)

    @property
    def A(self):
        return self.joystick.get_button(1)

    @property
    def B(self):
        return self.joystick.get_button(2)

    @property
    def Y(self):
        return self.joystick.get_button(3)

    @property
    def L(self):
        return self.joystick.get_button(4)

    @property
    def R(self):
        return self.joystick.get_button(5)

    @property
    def Z(self):
        return self.joystick.get_button(7)

    @property
    def START(self):
        return self.joystick.get_button(9)


class GamecubeControllerInputQueue(InputQueue):
    """
    A wrapper around GamecubeControllerReader and InputQueue which leaves all the fiddly
    input-reading logic to GamecubeControllerReader, and provides a convenient interface for
    accessing the queue of inputs.

    This allows games to subclass this class and define new key mappings e.g. "A" --> "attack"
    """

    def __init__(self, controller: GamecubeControllerReader, queue_length=5):
        super().__init__(queue_length)
        self.controller = controller

    def get_new_values(self):
        return self.controller.get_values()


if __name__ == "__main__":
    """ visual input checking. """

    class TextPrint(object):
        def __init__(self):
            self.reset()
            pygame.font.init()
            self.font = pygame.font.Font(None, 30)

        def tprint(self, screen, textString):
            textBitmap = self.font.render(textString, True, BLACK)
            screen.blit(textBitmap, (self.x, self.y))
            self.y += self.line_height

        def reset(self):
            self.x = 10
            self.y = 10
            self.line_height = 20

        def indent(self):
            self.x += 10

        def unindent(self):
            self.x -= 10

    BLACK = pygame.Color("black")
    WHITE = pygame.Color("white")

    pygame.joystick.init()
    textPrint = TextPrint()

    screen = pygame.display.set_mode((500, 700))
    pygame.display.set_caption("My Game")
    clock = pygame.time.Clock()
    done = False
    while not done:
        for event in pygame.event.get():  # User did something.
            if event.type == pygame.QUIT:  # If user clicked close.
                done = True  # Flag that we are done so we exit this loop.

        screen.fill(WHITE)
        textPrint.reset()
        controller = GamecubeControllerReader(joystick_id=0)

        textPrint.indent()
        textPrint.tprint(screen, "Gamecube controller 0")

        textPrint.tprint(screen, "Buttons:")
        textPrint.indent()
        for button in "A B X Y Z L R START".split():
            textPrint.tprint(screen, f"{button}: {getattr(controller, button)}")
        textPrint.unindent()

        textPrint.tprint(screen, "Axes:")
        textPrint.indent()
        for button in (
            "_L_TRIGGER_AXIS _R_TRIGGER_AXIS "
            "_GREY_STICK_X_AXIS _GREY_STICK_Y_AXIS "
            "_YELLOW_STICK_X_AXIS "
            "_YELLOW_STICK_Y_AXIS "
        ).split():
            textPrint.tprint(screen, f"{button}: {getattr(controller, button)}")
        textPrint.unindent()

        textPrint.tprint(screen, "Hats:")
        textPrint.indent()
        for button in "_D_PAD".split():
            textPrint.tprint(screen, f"{button}: {getattr(controller, button)}")
        textPrint.unindent()

        textPrint.tprint(screen, "PROCESSED INPUTS:")
        textPrint.indent()
        for button in (
            "GREY_STICK_LEFT GREY_STICK_RIGHT GREY_STICK_UP GREY_STICK_DOWN "
            "YELLOW_STICK_LEFT YELLOW_STICK_RIGHT YELLOW_STICK_UP YELLOW_STICK_DOWN "
            "R_AXIS L_AXIS "
            "D_PAD_LEFT D_PAD_RIGHT D_PAD_UP D_PAD_DOWN "
        ).split():
            textPrint.tprint(screen, f"{button}: {getattr(controller, button)}")
        textPrint.unindent()

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        # Limit to 20 frames per second.
        clock.tick(20)

    pygame.quit()
