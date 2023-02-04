import os
import unittest

import numpy as np

from src.visualizer import visualize


def test_visualize():
    cell_state = np.array(
        [
            [-1] * 16,
            [-1] * 16,
            [-1] * 16,
            [-1] * 16,
            [-1] * 16,
            [-1, -1, -1, -1, -1, 3, -1, -1, 3, 2, 2, 2, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, 3, 2, 2, 1, 0, 0, 1, 2, -1, -1, -1],
            [-1, -1, -1, -1, -1, 2, 0, 0, 0, 0, 1, 1, 2, -1, -1, -1],
            [-1, -1, -1, -1, -1, 2, 1, 0, 0, 0, 1, -1, 2, -1, -1, -1],
            [-1, -1, -1, -1, 2, -1, 2, 1, 1, 1, 2, 3, -1, -1, -1, -1],
            [-1, -1, -1, -1, 2, -1, 2, -1, -1, 1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, 1, 2, -1, -1, 1, 1, 2, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, 2, 2, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, 1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, 1, -1, -1, -1, -1, -1, -1, -1, -1],
        ]
    ).flatten()
    flags = np.zeros_like(cell_state, dtype=np.bool8)
    flags[[86, 87, 92, 139, 149]] = True
    visualize(cell_state, flags, 999)
    os.remove("demodata/demo999.png")


if __name__ == "__main__":
    unittest.main()