from __future__ import annotations

from abc import ABCMeta
from abc import abstractmethod
from copy import deepcopy

import numpy as np

from src.constants import CLOSED
from src.mine_sweeper import MineSweeper


class BasePlayer(metaclass=ABCMeta):
    def __init__(self, field: MineSweeper):
        """
        Attributes:
            field (MineSweeper):
                The mine sweeper field instance.
            H (int):
                The height of the field.
            W (int):
                The width of the field.
            n_open (int):
                The number of opened cells.
            neighbors (List[np.ndarray]):
                The indices of neighbors in each cell.
            flags (np.ndarray):
                The flag whether the corresponding cell has a mine or not.
            n_cells (int):
                The field size.
        """
        self._field = field
        self._W = field.width
        self._H = field.height
        self._n_cells = field.width * field.height
        self._n_open = 0
        self._neighbors = self._field.neighbors
        self._flags = np.zeros(self._W * self._H, dtype=np.bool8)

    @property
    def W(self) -> int:
        return self._W

    @property
    def H(self) -> int:
        return self._H

    @property
    def flags(self) -> np.ndarray:
        return deepcopy(self._flags)

    @property
    def over(self) -> bool:
        return self._field.over

    @property
    def clear(self) -> bool:
        return self._field.clear

    def _start(self, idx: int) -> None:
        self._field.start(idx)

    def _open(self, idx: int) -> None:
        self._field.open(idx)

    def _open_multiple(self, indices: np.ndarray) -> None:
        self._field.open_multiple(indices)

    def _build_flags(self) -> None:
        cell_state = self._field.cell_state
        cell_opened = cell_state != CLOSED
        target_indices = np.arange(self._n_cells)[cell_state > 0]
        for idx in target_indices:
            neighbor_indices = self._neighbors[idx]
            neighbors_closed = ~(cell_opened[neighbor_indices])
            n_closed = np.count_nonzero(neighbors_closed)
            if cell_state[idx] != n_closed:
                continue

            self._flags[neighbor_indices[neighbors_closed]] = True

    def _open_safe_cells(self) -> bool:
        cell_state = self._field.cell_state
        cell_opened = cell_state != CLOSED
        target_indices = np.arange(self._n_cells)[cell_state > 0]
        open_indices = []
        for idx in target_indices:
            neighbor_indices = self._neighbors[idx]
            n_flags = np.count_nonzero(self._flags[neighbor_indices])
            if cell_state[idx] != n_flags:
                continue

            open_indices.extend(neighbor_indices[~self._flags[neighbor_indices] & ~cell_opened[neighbor_indices]])

        if len(open_indices) > 0:
            self._open_multiple(np.unique(open_indices))

        return len(open_indices) > 0  # opened at least one cell or not

    def _open_land(self) -> None:
        cell_state = self._field.cell_state
        cell_closed = cell_state == CLOSED
        closed_indices = np.arange(self._n_cells)[cell_closed]
        for idx in closed_indices:
            neighbor_indices = self._neighbors[idx]
            n_closed = np.count_nonzero(cell_closed[neighbor_indices])
            if n_closed == neighbor_indices.size:
                self._open(idx)
                return

    @abstractmethod
    def _open_by_proba(self) -> None:
        raise NotImplementedError

    def solve(self) -> bool:
        idx = self._field.loc2idx(y=self.H // 2, x=self.W // 2)
        self._start(idx)

        while not self.over and not self.clear:
            self._build_flags()
            if not self._open_safe_cells():
                self._open_by_proba()

        return self.clear
