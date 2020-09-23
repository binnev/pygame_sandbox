import pygame

from base.inputs.queue import InputQueue


class KeyboardInputQueue(InputQueue):
    def get_new_values(self):
        return pygame.key.get_pressed()
