import pytest

from base.utils import count_edges, SparseMatrix, unzip


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


def test_unzip():
    a = (1, 2, 3, 4)
    b = (10, 20, 30, 40)
    c = (100, 200, 300, 400)
    zipped = list(zip(a, b, c))
    assert zipped == [
        (1, 10, 100),
        (2, 20, 200),
        (3, 30, 300),
        (4, 40, 400),
    ]
    assert unzip(zipped) == (a, b, c)


@pytest.mark.parametrize(
    "entries, expected_xlim, expected_ylim",
    [
        ([], (None, None), (None, None)),
        ([(2, 4)], (2, 2), (4, 4)),
        ([(2, 4), (3, 5)], (2, 3), (4, 5)),
        ([(10, 10), (-69, -420)], (-69, 10), (-420, 10)),
        ([(0, 0), (69, 420)], (0, 69), (0, 420)),
    ],
)
def test_sparse_matrix_xlim_ylim(entries, expected_xlim, expected_ylim):
    m = SparseMatrix({e: 1 for e in entries})
    assert m.xlim == expected_xlim
    assert m.ylim == expected_ylim


@pytest.mark.parametrize(
    "entries, expected_width, expected_height",
    [
        ([], 0, 0),
        ([(2, 4)], 1, 1),
        ([(2, 4), (3, 5)], 2, 2),
        ([(10, 10), (-69, -420)], 80, 431),
        ([(0, 0), (69, 420)], 70, 421),
    ],
)
def test_sparse_matrix_size_properties(entries, expected_width, expected_height):
    m = SparseMatrix({e: 1 for e in entries})
    assert m.width == expected_width
    assert m.height == expected_height
    assert m.size == (expected_width, expected_height)


def test_sparse_matrix_copy():
    m = SparseMatrix()
    m[(1, 1)] = True

    c = m.copy()
    assert isinstance(c, SparseMatrix)
    assert c[(1, 1)] is True
