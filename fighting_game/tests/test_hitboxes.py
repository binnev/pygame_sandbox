from unittest.mock import patch

import pygame
import pytest
from pygame.rect import Rect

from fighting_game.groups import Group
from fighting_game.objects import Hitbox, Entity, HitHandler

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
    assert h1.higher_priority_siblings == set()
    assert h1.lower_priority_siblings == {h2, h3}
    assert h1.siblings == {h2, h3}

    assert h2.higher_priority_sibling is h1
    assert h2.lower_priority_sibling is h3
    assert h2.higher_priority_siblings == {h1}
    assert h2.lower_priority_siblings == {h3}
    assert h2.siblings == {h1, h3}

    assert h3.higher_priority_sibling is h2
    assert h3.lower_priority_sibling is None
    assert h3.higher_priority_siblings == {h1, h2}
    assert h3.lower_priority_siblings == set()
    assert h3.siblings == {h1, h2}

    h1 = Hitbox(**kwargs)
    h2 = Hitbox(**kwargs, higher_priority_sibling=h1)
    h3 = Hitbox(**kwargs, higher_priority_sibling=h2)

    assert h1.higher_priority_sibling is None
    assert h1.lower_priority_sibling is h2
    assert h1.higher_priority_siblings == set()
    assert h1.lower_priority_siblings == {h2, h3}
    assert h1.siblings == {h2, h3}

    assert h2.higher_priority_sibling is h1
    assert h2.lower_priority_sibling is h3
    assert h2.higher_priority_siblings == {h1}
    assert h2.lower_priority_siblings == {h3}
    assert h2.siblings == {h1, h3}

    assert h3.higher_priority_sibling is h2
    assert h3.lower_priority_sibling is None
    assert h3.higher_priority_siblings == {h1, h2}
    assert h3.lower_priority_siblings == set()
    assert h3.siblings == {h1, h2}


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
    assert h1.siblings == set()

    # test I can set siblings to None
    h1.higher_priority_sibling = None
    assert h1.higher_priority_sibling is None
    h1.lower_priority_sibling = None
    assert h1.lower_priority_sibling is None
    assert h1.lower_priority_siblings == set()
    assert h1.higher_priority_siblings == set()
    assert h1.siblings == set()

    # test I can set siblings
    h2 = Hitbox(**kwargs)
    h3 = Hitbox(**kwargs)
    h2.higher_priority_sibling = h1
    h2.lower_priority_sibling = h3

    assert h2.higher_priority_sibling is h1
    assert h2.lower_priority_sibling is h3
    assert h2.higher_priority_siblings == {h1}
    assert h2.lower_priority_siblings == {h3}
    assert h2.siblings == {h1, h3}

    assert h1.higher_priority_sibling is None
    assert h1.lower_priority_sibling is h2
    assert h1.higher_priority_siblings == set()
    assert h1.lower_priority_siblings == {h2, h3}
    assert h1.siblings == {h2, h3}

    assert h3.higher_priority_sibling is h2
    assert h3.lower_priority_sibling is None
    assert h3.higher_priority_siblings == {h2, h1}
    assert h3.lower_priority_siblings == set()
    assert h3.siblings == {h2, h1}


def test_owner_position_inheritance():
    owner = Entity()
    owner.rect = Rect(6, 9, 0, 0)
    kwargs = dict(width=10, height=10, rotation=0, owner=owner)

    # hitbox should take its position from owner
    h1 = Hitbox(**kwargs)
    assert h1.x == 6
    assert h1.y == 9

    # update owner position; this should be reflected in hitbox
    owner.x = 10
    owner.y = 20
    assert owner.x == 10
    assert owner.y == 20
    assert h1.x == 10
    assert h1.y == 20

    # update hitbox offset; this should be reflected in relative position
    h1.x_offset = 5
    h1.y_offset = 10
    assert h1.x == 15
    assert h1.y == 30


@patch("fighting_game.objects.handle_hitbox_collision")
def test_handle_hits(mock):
    entity = Entity()
    entity.rect = Rect(0, 0, 10, 10)
    entity.x = 0
    entity.y = 0
    owner = Entity()
    owner.rect = Rect(0, 0, 0, 0)
    hit_handler = HitHandler()

    h1 = Hitbox(width=10, height=10, owner=owner)
    hitboxes = Group(h1)

    collisions = pygame.sprite.spritecollide(entity, hitboxes, dokill=False)
    assert len(collisions) == 1
    hit_handler.handle_hits(hitboxes, [entity])
    mock.assert_called_with(h1, entity)
    assert mock.call_count == 1


@patch("fighting_game.objects.handle_hitbox_collision")
def test_handle_hits_sibling_hitboxes_simultaneous(mock):
    entity = Entity()
    entity.rect = Rect(0, 0, 10, 10)
    entity.x = 0
    entity.y = 0
    owner = Entity()
    owner.rect = Rect(0, 0, 0, 0)

    h1 = Hitbox(width=10, height=10, owner=owner)
    h2 = Hitbox(width=10, height=10, owner=owner, higher_priority_sibling=h1)
    h3 = Hitbox(width=10, height=10, owner=owner, higher_priority_sibling=h2)

    # the order hitboxes are added to the group shouldn't matter
    for hitboxes in [
        Group(h1, h2),
        Group(h2, h1),
        Group(h1, h3),
        Group(h3, h1),
        Group(h3, h2, h1),
        Group(h2, h1, h3),
        Group(h1, h2, h3),
    ]:
        hit_handler = HitHandler()
        collisions = pygame.sprite.spritecollide(entity, hitboxes, dokill=False)
        assert len(collisions) == len(hitboxes)
        hit_handler.handle_hits(hitboxes, [entity])
        # h1, the higher priority hitbox, should always take priority
        mock.assert_called_with(h1, entity)
        with pytest.raises(AssertionError):
            mock.assert_called_with(h2, entity)
        with pytest.raises(AssertionError):
            mock.assert_called_with(h3, entity)
        # all hitboxes should be added to the handled list
        assert (h1, entity) in hit_handler.handled
        assert (h2, entity) in hit_handler.handled
        assert (h3, entity) in hit_handler.handled


@patch("fighting_game.objects.handle_hitbox_collision")
def test_handle_hits_sibling_hitboxes_later(mock):
    entity = Entity()
    entity.rect = Rect(0, 0, 10, 10)
    entity.x = 0
    entity.y = 0
    owner = Entity()
    owner.rect = Rect(0, 0, 0, 0)
    hit_handler = HitHandler()

    # h1 and h2 are related; h3 is standalone
    h1 = Hitbox(width=10, height=10, owner=owner)
    h2 = Hitbox(width=10, height=10, owner=owner, lower_priority_sibling=h1)
    h3 = Hitbox(width=10, height=10, owner=owner)

    # the first hitbox collides with the target
    hitboxes = Group(h1)
    collisions = pygame.sprite.spritecollide(entity, hitboxes, dokill=False)
    assert len(collisions) == 1
    hit_handler.handle_hits(hitboxes, [entity])
    mock.assert_called_with(h1, entity)
    with pytest.raises(AssertionError):
        mock.assert_called_with(h2, entity)
    with pytest.raises(AssertionError):
        mock.assert_called_with(h3, entity)
    assert mock.call_count == 1
    assert (h1, entity) in hit_handler.handled
    assert (h2, entity) in hit_handler.handled
    assert (h3, entity) not in hit_handler.handled

    # the next tick, another hitbox collides with the target. It is linked to h1 so should be
    # ignored.
    hitboxes = Group(h1, h2)
    collisions = pygame.sprite.spritecollide(entity, hitboxes, dokill=False)
    assert len(collisions) == 2
    hit_handler.handle_hits(hitboxes, [entity])
    with pytest.raises(AssertionError):
        mock.assert_called_with(h2, entity)
    assert mock.call_count == 1

    # the next tick, hitbox 3 is added. It has no siblings so it should connect
    hitboxes.add(h3)
    collisions = pygame.sprite.spritecollide(entity, hitboxes, dokill=False)
    assert len(collisions) == 3
    hit_handler.handle_hits(hitboxes, [entity])
    mock.assert_called_with(h3, entity)
    assert mock.call_count == 2
    assert (h1, entity) in hit_handler.handled
    assert (h2, entity) in hit_handler.handled
    assert (h3, entity) in hit_handler.handled
