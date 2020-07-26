import pytest
import numpy as np

from tetris.__main__ import Board


@pytest.mark.parametrize(
    "array, expected_result",
    [
        (np.array([[0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0],]), [2]),
        (np.array([[0, 0, 0, 0], [0, 0, 0, 0], [1, 0, 1, 1], [0, 0, 0, 0],]), []),
        (np.array([[0, 0, 1, 0], [0, 0, 1, 0], [1, 0, 1, 1], [0, 0, 1, 0],]), []),
    ],
)
def test_board_has_complete_rows(array, expected_result):
    board = Board(4, 4)
    board.array = array
    assert board.complete_lines == expected_result


@pytest.mark.parametrize(
    "array, row_to_clear, expected_result",
    [
        (
            np.array([[1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3], [4, 4, 4, 4]]),
            2,
            np.array([[0, 0, 0, 0], [1, 1, 1, 1], [2, 2, 2, 2], [4, 4, 4, 4]]),
        ),
        (
            np.array([[1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3], [4, 4, 4, 4]]),
            1,
            np.array([[0, 0, 0, 0], [1, 1, 1, 1], [3, 3, 3, 3], [4, 4, 4, 4]]),
        ),
        (
            np.array([[1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3], [4, 4, 4, 4]]),
            0,
            np.array([[0, 0, 0, 0], [2, 2, 2, 2], [3, 3, 3, 3], [4, 4, 4, 4]]),
        ),
    ],
)
def test_board_clear_row(array, row_to_clear, expected_result):
    board = Board(4, 4)
    board.array = array
    board.clear_row(row_to_clear)
    assert np.all(board.array == expected_result)
