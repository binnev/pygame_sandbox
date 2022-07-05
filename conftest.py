import pygame
import pytest


@pytest.fixture
def display_init():
    pygame.display.init()
    window = pygame.display.set_mode((1, 1))
    yield window
    pygame.quit()


@pytest.fixture
def font_init():
    pygame.display.init()
    pygame.font.init()
    yield
    pygame.quit()


@pytest.fixture(autouse=True)
def event_queue(monkeypatch):
    """auto-clear the event queue before every test"""
    monkeypatch.setattr("base.input.event.EventQueue.events", [])
