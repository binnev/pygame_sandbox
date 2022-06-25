from pygame.sprite import Sprite

from fighting_game.platforms import Platform


def test_platform_properties():

    plat = Platform(x=0, y=1, width=30, height=40)
    assert isinstance(plat, Sprite)

    assert plat.x == 0
    plat.x = 10
    assert plat.rect.centerx == 10
    assert plat.x == 10

    assert plat.y == 1
    plat.y = 15
    assert plat.rect.centery == 15
    assert plat.y == 15

    assert plat.rect.width == 30
    assert plat.rect.height == 40
