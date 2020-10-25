import pygame

from fighting_game.objects import Hitbox

pygame.display.init()
window = pygame.display.set_mode((50, 50))


def test_siblings_properties():

    h3 = Hitbox(x=0, y=0, width=10, height=10, rotation=0)
    h2 = Hitbox(x=0, y=0, width=10, height=10, rotation=0, lower_priority_sibling=h3)
    h1 = Hitbox(x=0, y=0, width=10, height=10, rotation=0, lower_priority_sibling=h2)

    assert h1.higher_priority_sibling is None
    assert h1.lower_priority_sibling is h2
    assert h2.higher_priority_sibling is h1
    assert h2.lower_priority_sibling is h3
    assert h3.higher_priority_sibling is h2
    assert h3.lower_priority_sibling is None

    assert h1.higher_priority_siblings == set()
    assert h1.lower_priority_siblings == {h2, h3}
    assert h2.higher_priority_siblings == {h1}
    assert h2.lower_priority_siblings == {h3}
    assert h3.higher_priority_siblings == {h1, h2}
    assert h3.lower_priority_siblings == set()

    h1 = Hitbox(x=0, y=0, width=10, height=10, rotation=0)
    h2 = Hitbox(x=0, y=0, width=10, height=10, rotation=0, higher_priority_sibling=h1)
    h3 = Hitbox(x=0, y=0, width=10, height=10, rotation=0, higher_priority_sibling=h2)

    assert h1.higher_priority_sibling is None
    assert h1.lower_priority_sibling is h2
    assert h2.higher_priority_sibling is h1
    assert h2.lower_priority_sibling is h3
    assert h3.higher_priority_sibling is h2
    assert h3.lower_priority_sibling is None

    assert h1.higher_priority_siblings == set()
    assert h1.lower_priority_siblings == {h2, h3}
    assert h2.higher_priority_siblings == {h1}
    assert h2.lower_priority_siblings == {h3}
    assert h3.higher_priority_siblings == {h1, h2}
    assert h3.lower_priority_siblings == set()


def test_none_siblings():
    h1 = Hitbox(x=0, y=0, width=10, height=10, rotation=0)
    assert h1.lower_priority_sibling is None
    assert h1.higher_priority_sibling is None
    assert h1.lower_priority_siblings == set()
    assert h1.higher_priority_siblings == set()

    h1.higher_priority_sibling = None
    assert h1.higher_priority_sibling is None
    h1.lower_priority_sibling = None
    assert h1.lower_priority_sibling is None
    assert h1.lower_priority_siblings == set()
    assert h1.higher_priority_siblings == set()

    h2 = Hitbox(x=0, y=0, width=10, height=10, rotation=0)
    h2.higher_priority_sibling = h1
    assert h2.higher_priority_sibling is h1
    assert h2.higher_priority_siblings == {h1}
    assert h2.lower_priority_sibling is None
    assert h2.lower_priority_siblings == set()
    assert h1.higher_priority_sibling is None
    assert h1.higher_priority_siblings == set()
    assert h1.lower_priority_sibling is h2
    assert h1.lower_priority_siblings == {h2}


