import pygame
import pytest


@pytest.fixture
def font_init():
    pygame.display.init()
    pygame.font.init()
    yield
    pygame.quit()


@pytest.fixture(autouse=True)
def event_queue(monkeypatch):
    """auto-clear the event queue before every test"""
    monkeypatch.setattr("robingame.input.event.EventQueue.events", [])
