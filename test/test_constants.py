import unittest

import numpy as np

from src.constants import SIZE, combination


def test_combination():
    vals = combination(5)
    a = [1, 5, 10, 10, 5, 1]
    ans = np.array(a + [0] * (SIZE - len(a)))
    assert np.allclose(vals, ans)


if __name__ == "__main__":
    unittest.main()
