from automata.utils import unzip, SparseMatrix


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


def test_sparse_matrix_size_properties():
    m = SparseMatrix()
    assert m.size == (0, 0)
    assert m.xlim == (0, 0)
    assert m.ylim == (0, 0)

    m[(50, 20)] = True
    assert m.size == (0, 0)
    assert m.xlim == (50, 50)
    assert m.ylim == (20, 20)

    m[(60, -20)] = True
    assert m.size == (10, 40)
    assert m.xlim == (50, 60)
    assert m.ylim == (-20, 20)


def test_sparse_matrix_copy():
    m = SparseMatrix()
    m[(1, 1)] = True

    c = m.copy()
    assert isinstance(c, SparseMatrix)
    assert c[(1, 1)] is True
