from typing import List, Tuple

import numpy as np

from src.constants import CellStates, CLOSED, COMBINATION, TargetData


MINE, NONE, SAFE = CellStates.mine.value, CellStates.none.value, CellStates.safe.value


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
        """
        Attributes:
            is_land (np.ndarray):
                Whether each cell does not involve the probability computation or not.
            n_flags_in_neighbors (np.ndarray):
                The numbers of flags around each cell.
                As these numbers are repeatedly used, we make a cache for them.
            n_closed_in_neighbors (np.ndarray):
                The numbers of non-target closed cells around each cell.
                As these numbers are repeatedly used, we make a cache for them.
            target_neighbors (np.ndarray):
                The indices of the target neighbors in the target.state array.
            states (np.ndarray):
                The states of each cell.
            counts (np.ndarray):
                The counts of how many times each cell has a mine.
            n_land_cells (int):
                The number of land cells.
            count4land (int):
                The counts of how many times each land cell has a mine.
            total_count (int):
                The counts of how many states we consider.
            opened_indices (int):
                The indices of opened cells.
            n_checked (int):
                Until what target we checked up to now.
                It is used for recursion.
        """
        self._cell_state = cell_state
        self._neighbors = neighbors
        self._n_flags = np.count_nonzero(flags)
        self._n_mines = n_mines
        self._n_cells = flags.size
        self._is_land = np.asarray(
            [
                cell_state[idx] == CLOSED and np.count_nonzero(cell_state[neighbors] == CLOSED) == len(neighbors)
                for idx, neighbors in enumerate(self._neighbors)
            ]
        )
        self._n_flags_in_neighbors: np.ndarray
        self._n_closed_in_neighbors: np.ndarray
        self._target_neighbors: np.ndarray
        self._states: np.ndarray
        self._counts: np.ndarray
        self._assumed: np.ndarray

        self._target = self._init_target(flags)
        self._n_land_cells = np.count_nonzero(self._is_land)
        self._count4land = 0
        self._total_count = 0
        self._opened_indices = np.arange(self._n_cells)[cell_state > 0]
        self._n_checked = 0

    def _init_target(self, flags: np.ndarray) -> TargetData:
        mask = (self._cell_state == CLOSED) & (~flags) & (~self._is_land)
        target_indices = np.arange(self._n_cells)[mask]
        self._states = np.full(target_indices.size, NONE, dtype=np.int32)
        self._counts = np.zeros(target_indices.size, dtype=np.float64)
        self._assumed = np.zeros(target_indices.size, dtype=np.bool8)
        target = TargetData(
            index=target_indices,
            proba=np.zeros(target_indices.size, dtype=np.float64),
        )
        rev = {idx: i for i, idx in enumerate(target_indices)}
        self._target_neighbors = [
            np.array([rev[idx] for idx in indices if idx in rev], dtype=np.int32) for indices in self._neighbors
        ]
        non_target_neighbors = [
            np.array([idx for idx in indices if idx not in rev], dtype=np.int32) for indices in self._neighbors
        ]
        self._n_flags_in_neighbors = np.array(
            [np.count_nonzero(flags[non_target_neighbors[i]]) for i in range(self._n_cells)]
        )
        self._n_closed_in_neighbors = np.array(
            [np.count_nonzero(self._cell_state[non_target_neighbors[i]] == CLOSED) for i in range(self._n_cells)]
        )

        return target

    def _add_count(self) -> None:
        new_mine_flags = self._states == MINE
        n_remaining_mines = self._n_mines - self._n_flags - np.count_nonzero(new_mine_flags)
        if n_remaining_mines < 0:  # contradiction
            return

        counts = COMBINATION[self._n_land_cells, n_remaining_mines]
        self._total_count += counts
        self._counts[new_mine_flags] += counts
        if n_remaining_mines - 1 >= 0 and self._n_land_cells - 1 >= 0:
            self._count4land += COMBINATION[self._n_land_cells - 1, n_remaining_mines - 1]

    def _update_target(self) -> None:
        assumed_indices = np.arange(self._n_checked, self._states.size)[self._assumed[self._n_checked:]]
        first_assumed_idx, last_assumed_idx = assumed_indices[0], assumed_indices[-1]
        self._states[last_assumed_idx] = SAFE
        self._states[last_assumed_idx + 1:] = NONE
        self._assumed[last_assumed_idx:] = False
        if first_assumed_idx == last_assumed_idx:
            self._n_checked = first_assumed_idx + 1
        if last_assumed_idx + 1 < self._states.size:
            self._states[last_assumed_idx + 1] = MINE
            self._assumed[last_assumed_idx + 1] = True

    def _assume_flags(self) -> Tuple[bool, bool]:
        assumed = False
        for idx in self._opened_indices:
            target_indices = self._target_neighbors[idx]
            ts = self._states[target_indices]
            n_closed = self._n_closed_in_neighbors[idx] + np.count_nonzero(ts != SAFE)
            if n_closed < self._cell_state[idx]:  # contradiction
                return True, False
            if self._cell_state[idx] == n_closed:
                neighbor_none_indices = target_indices[ts == NONE]
                self._states[neighbor_none_indices] = MINE
                assumed = neighbor_none_indices.size > 0

        return False, assumed

    def _assume_safe_cells(self) -> Tuple[bool, bool]:
        assumed = False
        for idx in self._opened_indices:
            target_indices = self._target_neighbors[idx]
            ts = self._states[target_indices]
            n_flags = self._n_flags_in_neighbors[idx] + np.count_nonzero(ts == MINE)
            if n_flags > self._cell_state[idx]:  # contradiction
                return True, False
            if n_flags == self._cell_state[idx]:
                neighbor_none_indices = target_indices[ts == NONE]
                self._states[neighbor_none_indices] = SAFE
                assumed = neighbor_none_indices.size > 0

        return False, assumed

    def _assume(self) -> bool:
        contradicted, assumed_flags = self._assume_flags()
        if contradicted:
            return False

        contradicted, assumed_safe_cells = self._assume_safe_cells()
        if contradicted:
            return False

        if assumed_flags or assumed_safe_cells:
            return True

        none_indices = np.where(self._states == NONE)[0]
        if none_indices.size > 0:  # new assumption
            self._states[none_indices[0]] = MINE
            self._assumed[none_indices[0]] = True
        else:
            self._add_count()
            self._update_target()

        return True

    def compute(self) -> Tuple[TargetData, float]:
        if self._states.size == 0:
            return self._target, 0.0

        t = 0
        self._states[0], self._assumed[0] = MINE, True
        while np.any(self._assumed) or NONE in self._states:
            t += 1
            if t % 10000 == 0:
                print(f"{t}: {self._n_checked}")

            if not self._assume():
                self._update_target()
                continue

        proba4land = 1.0
        if self._total_count != 0:
            self._target.proba = self._counts / self._total_count
            proba4land = self._count4land / self._total_count if self._n_land_cells != 0 else 1.0

        return self._target, proba4land
