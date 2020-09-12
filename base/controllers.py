import pygame


class GamecubeController:
    """ A handler class to map pygame's axis and button numbers to the gamecube's
    nomenclature. """

    # todo: put some mapping params to map joystick axes to 0--1?

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
    def L_AXIS(self):
        return self.joystick.get_axis(3)

    @property
    def R_AXIS(self):
        return self.joystick.get_axis(4)

    # =================== hat properties =======================

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
