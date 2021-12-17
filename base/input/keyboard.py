import pygame

from base.input.queue import InputQueue


class KeyboardInputQueue(InputQueue):
    def get_new_values(self):
        return pygame.key.get_pressed()
