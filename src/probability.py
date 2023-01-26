from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, Tuple
import numpy as np

from src.mine_sweeper import MineSweeper


SIZE = 500


def combination(n: int, size: int = SIZE) -> np.ndarray:
    ret = np.zeros(size, dtype=np.float64)
    ret[0] = 1.0
    for i in range(1, n + 1):
        ret[i] = ret[i - 1] / i * (n - i + 1)

    return ret


COMBINATION = np.array([combination(i) for i in range(SIZE)])


@dataclass
class TargetData:
    index: np.ndarray
    state: np.ndarray
    count: np.ndarray
    proba: np.ndarray
    rev: Dict[int, int]


class CellStates(IntEnum):
    safe = 0
    mine = 1
    assumed_mine = 2
    none = 3


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
        self._flags = flags
        self._n_flags = np.count_nonzero(flags)
        self._n_mines = self._field.n_mines
        self._n_cells = field.width * field.height
        self._is_land = np.asarray([
            self._cell_state[idx] == -1 and np.count_nonzero(self._cell_state[neighbors] == -1) == len(neighbors)
            for idx, neighbors in enumerate(self._neighbors)
        ])
        self._target = self._init_target()
        self._n_land_cells = np.count_nonzero(self._is_land)
        self._count4land = 0
        self._total_count = 0

        self.up_to_here = -1
        self.target = self._init_target()

    def _init_target(self) -> TargetData:
        mask = (self._cell_state == -1) & (~self._flags) & (~self._is_land)
        target_indices = np.arange(self._n_cells)[mask]

        return TargetData(
            index=target_indices,
            state=np.full(target_indices.size, CellStates.none.value, dtype=np.int32),
            count=np.zeros(target_indices.size, dtype=np.float64),
            proba=np.zeros(target_indices.size, dtype=np.float64),
            rev={idx: i for i, idx in enumerate(target_indices)},
        )

    def _add_count(self) -> None:
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

    def _renew_target(self) -> None:
        assumed_mine = CellStates.assumed_mine.value
        for i in range(self._target.state.size - 1, self.up_to_here, -1):
            if self._target.state[i] != assumed_mine:
                self._target.state[i] = CellStates.none.value
            else:
                self._target.state[i] = CellStates.safe.value
                if assumed_mine not in self._target.state[:i]:
                    self.up_to_here = i
                self._add_new_assumption()
                return

    def _count_new_neighbor_closed_cells(self, neighbor_indices: np.ndarray) -> int:
        return np.count_nonzero([
            self._target.state[self._target.rev[i]] != CellStates.safe.value
            if i in self._target.rev else
            self._cell_state[i] == -1
            for i in neighbor_indices
        ])

    def _count_new_neighbor_mines(self, neighbor_indices: np.ndarray) -> int:
        mine_idx = [CellStates.mine.value, CellStates.assumed_mine.value]
        return np.count_nonzero([
            self._target.state[self._target.rev[i]] in mine_idx
            if i in self._target.rev else
            self._flags[i]
            for i in neighbor_indices
        ])

    def _update_for_flag(self, neighbor_indices: np.ndarray) -> None:
        for idx in neighbor_indices:
            if idx not in self._target.rev:
                continue

            target_idx = self._target.rev[idx]
            if self._target.state[target_idx] == CellStates.none.value:
                self._target.state[target_idx] = CellStates.mine.value

    def _update_for_open(self, neighbor_indices: np.ndarray) -> bool:
        opened = False
        for idx in neighbor_indices:
            if idx not in self._target.rev:
                continue

            target_idx = self._target.rev[idx]
            if self._target.state[target_idx] == CellStates.none.value:
                self._target.state[target_idx] = CellStates.safe.value
                opened = True

        return opened

    def _build_flag(self) -> None:
        cell_state = self._cell_state
        target_indices = np.arange(self._n_cells)[cell_state > 0]
        for idx in target_indices:
            neighbor_indices = self._neighbors[idx]
            n_closed = self._count_new_neighbor_closed_cells(neighbor_indices)
            if n_closed < cell_state[idx]:  # contradiction
                self._renew_target()
                return
            elif cell_state[idx] == n_closed:
                self._update_for_flag(neighbor_indices)

    def _open_safe_cells(self) -> bool:
        cell_state = self._field.cell_state
        target_indices = np.arange(self._n_cells)[cell_state > 0]
        opened = False
        for idx in target_indices:
            neighbor_indices = self._neighbors[idx]
            n_flags = self._count_new_neighbor_mines(neighbor_indices)
            if cell_state[idx] != n_flags:
                continue
            if n_flags > cell_state[idx]:  # contradiction
                self._renew_target()
                return
            elif n_flags == cell_state[idx]:
                opened |= self._update_for_open(neighbor_indices)

        return opened

    def compute(self) -> Tuple[TargetData, float]:
        t = 0
        while (
            CellStates.assumed_mine.value in self._target.state or
            CellStates.none.value in self._target.state
        ):
            t += 1
            if t % 1000 == 0:
                print(f"{t}: {self.up_to_here}")

            self._build_flag()
            if self._open_safe_cells():
                continue

            if CellStates.none.value in self._target.state:
                self._add_new_assumption()
            else:
                self._add_count()
                self._renew_target()

        proba4land = 1.0
        if self._total_count != 0:
            self._target.proba = self._target.count / self._total_count
            proba4land = self._count4land / self._total_count if self._n_land_cells != 0 else 1.0

        return self._target, proba4land
