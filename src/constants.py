from dataclasses import dataclass
from enum import IntEnum

import numpy as np


SIZE = 500
DIRS = np.asarray([[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]])
CLOSED = -1


def combination(n: int, size: int = SIZE) -> np.ndarray:
    ret = np.zeros(size, dtype=np.float64)
    ret[0] = 1.0
    for i in range(1, n + 1):
        ret[i] = ret[i - 1] / i * (n - i + 1)

    return ret


COMBINATION = np.array([combination(i) for i in range(SIZE)])


@dataclass
class TargetData:
    """
    Attributes:
        index (np.ndarray):
            The indices of the target cells to check.
        proba (np.ndarray):
            The probability of each cell having a mine.
    """

    index: np.ndarray
    proba: np.ndarray


class Difficulties(IntEnum):
    easy = 0
    medium = 1
    hard = 2


class CellStates(IntEnum):
    """
    Attributes:
        safe (int):
            The cell does not have a mine.
        mine (int):
            The cell has a mine.
        none (int):
            The cell does not have any definition yet.
    """

    safe = 0
    mine = 1
    none = 2
