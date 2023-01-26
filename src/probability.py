from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List, Tuple
import numpy as np


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
        cell_state (np.ndarray):
                The state of each cell.
                    -1: Closed.
                     0: No mines around this cell.
                     1--8: The corresponding number of mines exist around this cell.
                The data is kept by 1D array, so we need to transform (y, x) --> y * w + x
        flags (np.ndarray):
                The flag whether the corresponding cell has a mine or not.
        neighbors (List[np.ndarray]):
            The indices of neighbors in each cell.
        n_mines (int):
            The number of mines in the field.
    """

    def __init__(
        self,
        cell_state: np.ndarray,
        flags: np.ndarray,
        neighbors: List[np.ndarray],
        n_mines: int,
    ):
        self._cell_state = cell_state
        self._neighbors = neighbors
        self._n_flags = np.count_nonzero(flags)
        self._n_mines = n_mines
        self._n_cells = flags.size
        self._is_land = np.asarray(
            [
                cell_state[idx] == -1 and np.count_nonzero(cell_state[neighbors] == -1) == len(neighbors)
                for idx, neighbors in enumerate(self._neighbors)
            ]
        )
        self._n_flags_in_neighbors: np.ndarray
        self._n_closed_in_neighbors: np.ndarray
        self._target_neighbors: np.ndarray

        self._target = self._init_target(flags)
        self._n_land_cells = np.count_nonzero(self._is_land)
        self._count4land = 0
        self._total_count = 0
        self._opened_indices = np.arange(self._n_cells)[cell_state > 0]
        self._n_checked = 0

    def _init_target(self, flags: np.ndarray) -> TargetData:
        mask = (self._cell_state == -1) & (~flags) & (~self._is_land)
        target_indices = np.arange(self._n_cells)[mask]
        target = TargetData(
            index=target_indices,
            state=np.full(target_indices.size, CellStates.none.value, dtype=np.int32),
            count=np.zeros(target_indices.size, dtype=np.float64),
            proba=np.zeros(target_indices.size, dtype=np.float64),
            rev={idx: i for i, idx in enumerate(target_indices)},
        )
        self._target_neighbors = [
            np.array([target.rev[idx] for idx in indices if idx in target.rev], dtype=np.int32)
            for indices in self._neighbors
        ]
        non_target_neighbors = [
            np.array([idx for idx in indices if idx not in target.rev], dtype=np.int32)
            for indices in self._neighbors
        ]
        self._n_flags_in_neighbors = np.array(
            [np.count_nonzero(flags[non_target_neighbors[i]]) for i in range(self._n_cells)]
        )
        self._n_closed_in_neighbors = np.array(
            [np.count_nonzero(self._cell_state[non_target_neighbors[i]] == -1) for i in range(self._n_cells)]
        )

        return target

    def _add_count(self) -> None:
        new_mine_flags = (self._target.state == CellStates.mine.value) | (
            self._target.state == CellStates.assumed_mine.value
        )
        n_remaining_mines = self._n_mines - self._n_flags - np.count_nonzero(new_mine_flags)
        counts = COMBINATION[self._n_land_cells, n_remaining_mines]
        self._count4land += COMBINATION[self._n_land_cells - 1, n_remaining_mines - 1]
        self._total_count += counts
        self._target.count[new_mine_flags] += counts

    def _update_target(self) -> None:
        assumed_mine = CellStates.assumed_mine.value
        assumed_indices = np.arange(self._n_checked, self._target.state.size)[
            self._target.state[self._n_checked:] == assumed_mine
        ]
        first_assumed_idx, last_assumed_idx = assumed_indices[0], assumed_indices[-1]
        self._target.state[last_assumed_idx] = CellStates.safe.value
        self._target.state[last_assumed_idx + 1:] = CellStates.none.value
        if first_assumed_idx == last_assumed_idx:
            self._n_checked = first_assumed_idx + 1
        if last_assumed_idx + 1 < self._target.state.size:
            self._target.state[last_assumed_idx + 1] = assumed_mine

    def _assume_flags(self) -> bool:
        safe, mine, none = CellStates.safe.value, CellStates.mine.value, CellStates.none.value
        for idx in self._opened_indices:
            target_indices = self._target_neighbors[idx]
            ts = self._target.state[target_indices]
            n_closed = self._n_closed_in_neighbors[idx] + np.count_nonzero(ts != safe)
            if n_closed < self._cell_state[idx]:  # contradiction
                return True
            if self._cell_state[idx] == n_closed:
                neighbor_none_indices = target_indices[ts == none]
                self._target.state[neighbor_none_indices] = mine

        return False

    def _assume_safe_cells(self) -> Tuple[bool, bool]:
        mine, assumed_mine, none = CellStates.mine.value, CellStates.assumed_mine.value, CellStates.none.value
        assumed = False
        for idx in self._opened_indices:
            target_indices = self._target_neighbors[idx]
            ts = self._target.state[target_indices]
            n_flags = self._n_flags_in_neighbors[idx] + np.count_nonzero((ts == mine) | (ts == assumed_mine))
            if n_flags > self._cell_state[idx]:  # contradiction
                return True, False
            if n_flags == self._cell_state[idx]:
                neighbor_none_indices = target_indices[ts == none]
                self._target.state[neighbor_none_indices] = CellStates.safe.value
                assumed |= neighbor_none_indices.size > 0

        return False, assumed

    def _assume(self) -> bool:
        contradicted = self._assume_flags()
        if contradicted:
            return False

        contradicted, assumed = self._assume_safe_cells()
        if contradicted:
            return False

        if assumed:
            return True

        none_indices = np.where(self._target.state == CellStates.none.value)[0]
        if none_indices.size > 0:  # new assumption
            self._target.state[none_indices[0]] = CellStates.assumed_mine.value
        else:
            self._add_count()
            self._update_target()

        return True

    def compute(self) -> Tuple[TargetData, float]:
        if self._target.state.size == 0:
            return self._target, 0.0

        t = 0
        self._target.state[0] = CellStates.assumed_mine.value
        while CellStates.assumed_mine.value in self._target.state or CellStates.none.value in self._target.state:
            t += 1
            if t % 1000 == 0:
                print(f"{t}: {self._n_checked}")

            if not self._assume():
                self._update_target()
                continue

        proba4land = 1.0
        if self._total_count != 0:
            self._target.proba = self._target.count / self._total_count
            proba4land = self._count4land / self._total_count if self._n_land_cells != 0 else 1.0

        return self._target, proba4land
