import pygame


class GamecubeController:
    """ A handler class to map pygame's axis and button numbers to the gamecube's
    nomenclature. """

    ANALOG_MAGNITUDE = 0.86  # max output value of the analog stick
    CSTICK_MAGNITUDE = 0.86  # max output value of the C stick

    def __init__(self, joystick_id):
        self.joystick_id = joystick_id
        # get the joystick from pygame
        self.joystick = pygame.joystick.Joystick(joystick_id)
        # switch on the joystick
        self.joystick.init()

    # =================== axis properties =======================

    @property
    def ANALOG_X(self):
        return self.joystick.get_axis(0)

    @property
    def ANALOG_Y(self):
        return self.joystick.get_axis(1)

    @property
    def CSTICK_X(self):
        return self.joystick.get_axis(5)

    @property
    def CSTICK_Y(self):
        return self.joystick.get_axis(2)

    @property
    def _L_AXIS(self):
        return self.joystick.get_axis(3)

    @property
    def _R_AXIS(self):
        return self.joystick.get_axis(4)

    def _normalise(self, value, normalising_parameter, cap=1.0):
        """ Return the normalised, absolute, capped value """
        normalised_value = abs(value) / normalising_parameter
        return min(normalised_value, cap)

    @property
    def ANALOG_LEFT(self):
        return self._normalise(self.ANALOG_X, self.ANALOG_MAGNITUDE) if self.ANALOG_X < 0 else 0.0

    @property
    def ANALOG_RIGHT(self):
        return self._normalise(self.ANALOG_X, self.ANALOG_MAGNITUDE) if self.ANALOG_X > 0 else 0.0

    @property
    def ANALOG_UP(self):
        return self._normalise(self.ANALOG_Y, self.ANALOG_MAGNITUDE) if self.ANALOG_Y < 0 else 0.0

    @property
    def ANALOG_DOWN(self):
        return self._normalise(self.ANALOG_Y, self.ANALOG_MAGNITUDE) if self.ANALOG_Y > 0 else 0.0

    @property
    def CSTICK_LEFT(self):
        return self._normalise(self.CSTICK_X, self.CSTICK_MAGNITUDE) if self.CSTICK_X < 0 else 0.0

    @property
    def CSTICK_RIGHT(self):
        return self._normalise(self.CSTICK_X, self.CSTICK_MAGNITUDE) if self.CSTICK_X > 0 else 0.0

    @property
    def CSTICK_UP(self):
        return self._normalise(self.CSTICK_Y, self.CSTICK_MAGNITUDE) if self.CSTICK_Y < 0 else 0.0

    @property
    def CSTICK_DOWN(self):
        return self._normalise(self.CSTICK_Y, self.CSTICK_MAGNITUDE) if self.CSTICK_Y > 0 else 0.0

    def _normalise_trigger(self):
        pass

    @property
    def R_AXIS(self):
        return self._normalise_trigger(self._R_AXIS, self.TRIGGER_MAGNITUDE)

    @property
    def L_AXIS(self):
        return self._normalise_trigger(self.CSTICK_Y, self.TRIGGER_MAGNITUDE)

    # =================== hat properties =======================

    @property
    def D_PAD(self):
        return self.joystick.get_hat(0)

    # =================== button properties =======================

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


if __name__ == "__main__":

    class TextPrint(object):
        def __init__(self):
            self.reset()
            pygame.font.init()
            self.font = pygame.font.Font(None, 20)

        def tprint(self, screen, textString):
            textBitmap = self.font.render(textString, True, BLACK)
            screen.blit(textBitmap, (self.x, self.y))
            self.y += self.line_height

        def reset(self):
            self.x = 10
            self.y = 10
            self.line_height = 15

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
        controller = GamecubeController(joystick_id=0)

        textPrint.indent()
        textPrint.tprint(screen, "Gamecube controller 0")

        textPrint.tprint(screen, "Buttons:")
        textPrint.indent()
        for button in "A B X Y Z L R START".split():
            textPrint.tprint(screen, f"{button}: {getattr(controller, button)}")
        textPrint.unindent()

        textPrint.tprint(screen, "Axes:")
        textPrint.indent()
        for button in "L_AXIS R_AXIS ANALOG_X ANALOG_Y CSTICK_X CSTICK_Y".split():
            textPrint.tprint(screen, f"{button}: {getattr(controller, button)}")
        textPrint.tprint(screen, "---")
        for button in (
            "ANALOG_LEFT ANALOG_RIGHT ANALOG_UP ANALOG_DOWN "
            "CSTICK_LEFT CSTICK_RIGHT CSTICK_UP CSTICK_DOWN "
        ).split():
            textPrint.tprint(screen, f"{button}: {getattr(controller, button)}")
        textPrint.unindent()

        textPrint.tprint(screen, "Hats:")
        textPrint.indent()
        for button in "D_PAD".split():
            textPrint.tprint(screen, f"{button}: {getattr(controller, button)}")
        textPrint.unindent()

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        # Limit to 20 frames per second.
        clock.tick(20)

    pygame.quit()
