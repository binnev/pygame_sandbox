import numpy as np
import pytest

from connect4.connect4 import winner, slice_winner


@pytest.mark.parametrize(
    "input, expected_result",
    [
        ([0, 0, 0, 0, 0, 0, 0, 0], None),
        ([0, 0, 0, 0, 1, 1, 1, 0], None),
        ([0, 0, 0, 0, 1, 1, 1, 1], 1),
        ([0, 0, 0, 1, 1, 0, 1, 1], None),
        ([2, 2, 2, 1, 1, 2, 1, 1], None),
        ([2, 2, 2, 2, 1, 2, 1, 1], 2),
        ([2, 2, 1], None),
    ],
)
def test_slice_winner(input, expected_result):
    assert slice_winner(input) == expected_result


@pytest.mark.parametrize(
    "board, expected_result",
    [
        (np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]), 1),
        (np.array([[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]), None),
        (np.array([[1, 0, 2, 0], [0, 2, 0, 0], [2, 0, 1, 0], [0, 0, 0, 1]]), None),
        (np.array([[1, 0, 2, 1], [0, 2, 1, 0], [2, 1, 1, 0], [1, 0, 0, 1]]), 1),
        (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 1],
                    [0, 0, 0, 1, 0],
                    [0, 0, 1, 0, 0],
                    [0, 1, 0, 0, 0],
                ]
            ),
            1,
        ),
        (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [2, 0, 0, 0, 1],
                    [0, 2, 0, 1, 0],
                    [0, 0, 2, 0, 0],
                    [0, 1, 0, 2, 0],
                ]
            ),
            2,
        ),
        (
            np.array(
                [
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 1, 2, 0, 1, 0, 0, 0, 0, 0, 0],
                    [1, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0],
                ]
            ),
            1,
        ),
    ],
)
def test_winner(board, expected_result):
    assert winner(board) == expected_result
