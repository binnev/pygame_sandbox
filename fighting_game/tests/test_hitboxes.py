from fighting_game.objects import get_lower_priority_siblings


def test_get_siblings():
    class Hitbox:
        def __init__(self, name, lower_priority_sibling=None):
            self.lower_priority_sibling = lower_priority_sibling
            self.name = name

        def __repr__(self):
            return f"{self.name}"

    h3 = Hitbox("h3")
    h2 = Hitbox("h2", h3)
    h1 = Hitbox("h1", h2)

    assert h1.lower_priority_sibling is h2
    assert h2.lower_priority_sibling is h3
    assert h3.lower_priority_sibling is None

    output = get_lower_priority_siblings(h1)
    assert output == [h2, h3]

    output = get_lower_priority_siblings(h2)
    assert output == [h3]

    output = get_lower_priority_siblings(h3)
    assert output == []
