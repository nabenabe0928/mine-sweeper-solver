from copy import deepcopy
from dataclasses import dataclass
from enum import IntEnum
import numpy as np

from py.mine_sweeper import MineSweeper


@dataclass
class TargetData:
    index: np.ndarray
    state: np.ndarray
    count: np.ndarray


class CellStates(IntEnum):
    safe = 0
    mine = 1
    assumed_mine = 2
    none = 3


def combination(n: int, r: int) -> float:
    c = 1.0
    mul = [k for k in range(n, n - r, -1)]
    for i, m in enumerate(mul):
        c *= float(m) / float(i + 1)

    return c


COMBINATION = np.array([[combination(i, j) if i >= j else 0.0 for i in range(1000)] for j in range(1000)])


class ProbabilityCalculator:
    """
    This class computes the probability of having a mine in each cell.

    Args:
        field (MineSweeper):
            The mine sweeper field instance.
        flags (np.ndarray):
                The flag whether the corresponding cell has a mine or not.
    """
    def __init__(self, field: MineSweeper, flags: np.ndarray):
        self._field = field
        self._cell_state = field.cell_state
        self._neighbors = field.neighbors
        self._flags = deepcopy(flags)
        self._n_flags = np.count_nonzero(flags)
        self._n_mines = self.field.n_mines
        self._W = field.width
        self._H = field.height
        self._is_land = np.asarray([
            np.count_nonzero(self._cell_state[neighbors] == -1) == len(neighbors)
            for neighbors in self._neighbors
        ])
        self._target = self._init_target()
        self._n_land_cells = np.count_nonzero(self._is_land)
        self._count4land = 0
        self._total_count = 0

        self.up_to_here = -1
        self.target = self.init_target()
        self.n_none = self.target[1].count(None)

    def _init_target(self) -> TargetData:
        mask = (self._cell_state == -1) & (~self._flags) & (~self._is_land)
        target_indices = np.arange(self.W * self.H)[mask]

        return TargetData(
            index=target_indices,
            state=np.full(target_indices.size, CellStates.none.value),
            count=np.zeros(target_indices.size),
        )

    def GetFlag(self):
        for w in range(self.W):
            for h in range(self.H):
                if self._field.GetCellInfo(w, h) != -1:
                    count = 0
                    around = self._field.around(w, h)
                    for a in around:
                        num = self.position_to_num(a[0], a[1])
                        if num in self.target[0]:
                            idx = self.target[0].index(num)
                            if self.target[1][idx] != 0:
                                count += 1
                        else:
                            if self._field.GetCellInfo(a[0], a[1]) == -1:
                                count += 1

                    if count == self._field.GetCellInfo(w, h):
                        for a in around:
                            num = self.position_to_num(a[0], a[1])
                            if num in self.target[0]:
                                idx = self.target[0].index(num)
                                if self.target[1][idx] != 0 and self.target[1][idx] != 2:
                                    self.target[1][idx] = 1
                    elif count < self._field.GetCellInfo(w, h):
                        self.renew_target()
                        return None

    def build_flag(self) -> None:
        cell_state = self._cell_state
        cell_opened = (cell_state != -1)
        target_indices = np.arange(self._n_cells)[cell_state > 0]
        for idx in target_indices:
            """
                    count = 0
                    for a in around:
                        if num in self.target[0]:
                            idx = self.target[0].index(num)
                            if self.target[1][idx] != 0:
                                count += 1
                        else:
                            if self._field.GetCellInfo(a[0], a[1]) == -1:
                                count += 1
            """
            neighbor_indices = self._neighbors[idx]
            neighbors_closed = ~(cell_opened[neighbor_indices])
            n_closed = np.count_nonzero(neighbors_closed)
            if cell_state[idx] == n_closed:
                self._flags[neighbor_indices[neighbors_closed]] = True

    def open_safe_cells(self) -> None:
        cell_state = self._field.cell_state
        cell_opened = (cell_state != -1)
        target_indices = np.arange(self._n_cells)[cell_opened]
        for idx in target_indices:
            neighbor_indices = self._neighbors[idx]
            n_flags = np.count_nonzero(self._flags[neighbor_indices])
            if cell_state[idx] != n_flags:
                continue

            for target_idx in neighbor_indices:
                if not self._flags[target_idx] and not cell_opened[target_idx]:
                    y, x = self._field.idx2loc(target_idx)
                    self._field.open(y, x)

    def OpenSafe(self):
        for w in range(self.W):
            for h in range(self.H):
                if self._field.GetCellInfo(w, h) != -1:
                    count = 0
                    around = self._field.around(w, h)
                    for a in around:
                        num = self.position_to_num(a[0], a[1])
                        if num in self.target[0]:
                            idx = self.target[0].index(num)
                            if self.target[1][idx] == 1 or self.target[1][idx] == 2:
                                count += 1
                        else:
                            if self._flags[a[0]][a[1]]:
                                count += 1

                    if count == self._field.GetCellInfo(w, h):
                        for a in around:
                            num = self.position_to_num(a[0], a[1])
                            if num in self.target[0]:
                                idx = self.target[0].index(num)

                                if self.target[1][idx] != 1 and self.target[1][idx] != 2:
                                    self.target[1][idx] = 0
                    elif count > self._field.GetCellInfo(w, h):
                        self.renew_target()
                        return None

    def count_patterns(self) -> None:
        new_mine_flags = (self._target.state == 1) | (self._target.state == 2)
        n_remaining_mines = self._n_mines - self._n_flags - np.count_nonzero(new_mine_flags)
        counts = COMBINATION[self._n_land_cells, n_remaining_mines]
        self._count4land += COMBINATION[self._n_land_cells - 1, n_remaining_mines - 1]
        self._total_count += counts
        self._target.count[new_mine_flags] += counts

    def _add_new_assumption(self) -> None:
        none_indices = np.arange(self._target.state.size)[self._target.state == CellStates.none.value]
        if none_indices.size > 0:
            self._target.state[none_indices[0]] = CellStates.assumed_mine.value

    def renew_target(self):
        for i in range(len(self.target[1]) - 1, self.up_to_here, -1):
            if self.target[1][i] != 2:
                self.target[1][i] = None
            else:
                self.target[1][i] = 0
                if 2 not in self.target[1][:i]:
                    self.up_to_here = i
                self._add_new_assumption()
                return None

    def cannot_open(self):
        n_none = self.target[1].count(None)
        if n_none == self.n_none:
            return True
        else:
            self.n_none = n_none
            return False

    def compute(self):
        t = 0
        while 2 in self.target[1] or None in self.target[1]:
            t += 1
            if t % 100 == 0:
                print("{}: {}".format(t, self.up_to_here))
            self.GetFlag()
            self.OpenSafe()

            if self.cannot_open():
                if self.n_none != 0:
                    self._add_new_assumption()
                else:
                    self.count_patterns()
                    self.renew_target()

        if self.count != 0:
            self.target[2] = np.asarray(self.target[2]) / self.count

            if self.L != 0:
                self.countL /= self.count
            else:
                self.countL = 1.0

        return self.target, self.countL
