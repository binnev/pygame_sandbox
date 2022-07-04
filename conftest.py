import pygame
import pytest


@pytest.fixture
def display_init():
    pygame.display.init()
    window = pygame.display.set_mode((1, 1))
    yield window
    pygame.quit()
