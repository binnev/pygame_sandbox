import pytest

from automata.gravity.vector import Vector2D


@pytest.mark.parametrize(
    "vector, expected_magnitude",
    [
        (Vector2D(3, 4), 5.0),
        (Vector2D(-3, -4), 5.0),
        (Vector2D(1, 0), 1.0),
        (Vector2D(0, 1), 1.0),
    ],
)
def test_magnitude(vector, expected_magnitude):
    assert vector.magnitude() == expected_magnitude


@pytest.mark.parametrize(
    "vector, expected_unit_vector",
    [
        (Vector2D(1, 1), Vector2D(0.7071067811, 0.7071067811)),
        (Vector2D(10, 10), Vector2D(0.7071067811, 0.7071067811)),
        (Vector2D(3, 4), Vector2D(0.6, 0.8)),
        (Vector2D(3, -4), Vector2D(0.6, -0.8)),
        (Vector2D(-3, 4), Vector2D(-0.6, 0.8)),
        (Vector2D(-3, -4), Vector2D(-0.6, -0.8)),
    ],
)
def test_unit(vector, expected_unit_vector):
    unit = vector.unit()
    assert unit.dx == pytest.approx(expected_unit_vector.dx, 0.00001)
    assert unit.dy == pytest.approx(expected_unit_vector.dy, 0.00001)


@pytest.mark.parametrize(
    "vector, expected_reversed",
    [
        (Vector2D(0, 0), Vector2D(0, 0)),
        (Vector2D(1, 1), Vector2D(-1, -1)),
        (Vector2D(1, -1), Vector2D(-1, 1)),
        (Vector2D(-1, 1), Vector2D(1, -1)),
        (Vector2D(-1, -1), Vector2D(1, 1)),
    ],
)
def test_reverse(vector, expected_reversed):
    assert vector.reverse() == expected_reversed
