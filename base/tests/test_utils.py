import pytest

from base.utils import count_edges


@pytest.mark.parametrize(
    "input, expected_rising_edges, expected_falling_edges",
    [
        ([], 0, 0),
        ([0], 0, 0),
        ([1], 0, 0),
        ([0, 0], 0, 0),
        ([1, 1], 0, 0),
        ([0, 1], 1, 0),
        ([1, 0], 0, 1),
        ([1, 1, 1, 1, 1, 1], 0, 0),
        ([1, 0, 1, 1, 1, 1], 1, 1),
        ([1, 0, 1, 1, 0, 1], 2, 2),
        ([1, 0, 1, 0, 0, 1], 2, 2),
        ([0, 0, 0, 0, 0, 0, 0, 1], 1, 0),
        ([1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0], 0, 1),
        ([0, 0, 0, 0, 0.6, 0, 0, 0], 1, 1),
    ],
)
def test_count_edges(input, expected_rising_edges, expected_falling_edges):
    rising, falling = count_edges(input)
    assert rising == expected_rising_edges
    assert falling == expected_falling_edges
