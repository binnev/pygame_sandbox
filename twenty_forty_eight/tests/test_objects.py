import pytest
from twenty_forty_eight.objects import slide_row_left, add_pairs


@pytest.mark.parametrize(
    "row, output",
    [
        ([2, 2], [4]),
        ([2], [2]),
        ([], []),
        ([4, 2], [4, 2]),
        ([2, 2, 2], [4, 2]),
        ([4, 2, 2], [4, 4]),
        ([2, 2, 4], [4, 4]),
    ],
)
def test_add_pairs(row, output):
    assert add_pairs(row) == output


@pytest.mark.parametrize(
    "row, output",
    [
        ([0, 2, 0, 2, 0, 0], [4, 0, 0, 0, 0, 0]),
        ([0, 0, 2, 0], [2, 0, 0, 0]),
        ([2, 0, 0, 0], [2, 0, 0, 0]),
        ([0, 0, 0, 0, 2, 2], [4, 0, 0, 0, 0, 0]),
        ([0, 4, 2, 0, 0, 0], [4, 2, 0, 0, 0, 0]),
        ([0, 0, 0, 0], [0, 0, 0, 0]),
        ([2, 2, 2, 0], [4, 2, 0, 0]),
        ([4, 2, 2], [4, 4, 0]),
        ([2, 2, 4], [4, 4, 0]),
    ],
)
def test_slide_row_left(row, output):
    assert slide_row_left(row) == output
