import pygame
from pygame.rect import Rect

from fighting_game.objects import Hitbox, Platform, Entity

pygame.display.init()
window = pygame.display.set_mode((50, 50))


def test_siblings_set_at_init():
    owner = Entity()
    owner.rect = Rect(0, 0, 0, 0)
    kwargs = dict(width=10, height=10, rotation=0, owner=owner)
    h3 = Hitbox(**kwargs)
    h2 = Hitbox(**kwargs, lower_priority_sibling=h3)
    h1 = Hitbox(**kwargs, lower_priority_sibling=h2)

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

    h1 = Hitbox(**kwargs)
    h2 = Hitbox(**kwargs, higher_priority_sibling=h1)
    h3 = Hitbox(**kwargs, higher_priority_sibling=h2)

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


def test_setting_siblings_properties():
    owner = Entity()
    owner.rect = Rect(0, 0, 0, 0)
    kwargs = dict(width=10, height=10, rotation=0, owner=owner)

    # no siblings expected output
    h1 = Hitbox(**kwargs)
    assert h1.lower_priority_sibling is None
    assert h1.higher_priority_sibling is None
    assert h1.lower_priority_siblings == set()
    assert h1.higher_priority_siblings == set()

    # test I can set siblings to None
    h1.higher_priority_sibling = None
    assert h1.higher_priority_sibling is None
    h1.lower_priority_sibling = None
    assert h1.lower_priority_sibling is None
    assert h1.lower_priority_siblings == set()
    assert h1.higher_priority_siblings == set()

    # test I can set siblings
    h2 = Hitbox(**kwargs)
    h3 = Hitbox(**kwargs)
    h2.higher_priority_sibling = h1
    h2.lower_priority_sibling = h3

    assert h2.higher_priority_sibling is h1
    assert h2.higher_priority_siblings == {h1}
    assert h2.lower_priority_sibling is h3
    assert h2.lower_priority_siblings == {h3}

    assert h1.higher_priority_sibling is None
    assert h1.higher_priority_siblings == set()
    assert h1.lower_priority_sibling is h2
    assert h1.lower_priority_siblings == {h2, h3}

    assert h3.higher_priority_sibling is h2
    assert h3.higher_priority_siblings == {h2, h1}
    assert h3.lower_priority_sibling is None
    assert h3.lower_priority_siblings == set()


def test_owner_position_inheritance():
    owner = Entity()
    owner.rect = Rect(6, 9, 0, 0)
    kwargs = dict(width=10, height=10, rotation=0, owner=owner)

    h1 = Hitbox(**kwargs)
    assert h1.x == 6
    assert h1.y == 9

    owner.x = 10
    owner.y = 20
    assert owner.x == 10
    assert owner.y == 20
    assert h1.x == 10
    assert h1.y == 20

    h1.x_offset = 5
    h1.y_offset = 10
    assert h1.x == 15
    assert h1.y == 30
