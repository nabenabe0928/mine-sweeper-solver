from __future__ import annotations

from collections import deque
from copy import deepcopy
from typing import Literal

import numpy as np

from src.constants import CLOSED, DIRS


class MineSweeper:
    """
    The mine sweeper field object.
    Args:
        difficulty (Literal[0, 1, 2]):
            The difficulty of the game.
            0 (easy):
                9 x 9 cells with 10 mines.
            1 (medium):
                16 x 16 cells with 40 mines.
            2 (hard):
                30 x 16 cells with 100 mines.
        seed (int | None):
            The random seed.
        plot_field (bool):
            Whether to print the field each round.
    """

    def __init__(self, difficulty: Literal[0, 1, 2] = 0, seed: int | None = None, plot_field: bool = True):
        """
        Attributes:
            width (int):
                The width of the field.
            height (int):
                The height of the field.
            n_mines (int):
                The number of mines in the field.
            field (np.ndarray):
                The ground truth of each cell.
                    -2: A mine.
                     0: No mines around this cell.
                     1--8: The corresponding number of mines exist around this cell.
                The data is kept by 1D array, so we need to transform (y, x) --> y * w + x
            cell_state (np.ndarray):
                The state of each cell.
                    -1: Closed.
                     0: No mines around this cell.
                     1--8: The corresponding number of mines exist around this cell.
                The data is kept by 1D array, so we need to transform (y, x) --> y * w + x
            neighbors (List[np.ndarray]):
                The indices of neighbors in each cell.
        """
        self._rng = np.random.RandomState(seed)
        self._width = [9, 16, 30][difficulty]
        self._height = [9, 16, 16][difficulty]
        self._n_mines = [10, 40, 100][difficulty]
        self._field = np.zeros(self.height * self.width, dtype=np.int32)
        self._cell_state = CLOSED * np.ones(self.height * self.width, dtype=np.int32)
        self._neighbors = [
            np.asarray([self.loc2idx(y, x) for (y, x) in self.idx2loc(i) + DIRS if not self._out_of_field(y, x)])
            for i in range(self.height * self.width)
        ]
        self._plot_field = plot_field
        self._over = False
        self._clear = False
        self._terminated = False

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def n_mines(self) -> int:
        return self._n_mines

    @property
    def over(self) -> bool:
        return self._over

    @property
    def clear(self) -> bool:
        return self._clear

    @property
    def cell_state(self) -> np.ndarray:
        return deepcopy(self._cell_state)

    @property
    def neighbors(self) -> list[np.ndarray]:
        return deepcopy(self._neighbors)

    def loc2idx(self, y: int, x: int) -> int:
        if self._out_of_field(y, x):
            raise ValueError(f"(y, x) must be in [0, {self.height}) x [0, {self.width}), but got ({y}, {x})")

        return self.width * y + x

    def idx2loc(self, idx: int) -> np.ndarray:
        size = self.width * self.height
        if idx < 0 or idx >= self.width * self.height:
            raise ValueError(f"idx must be in [0, HW) = [0, {size}), but got {idx}")

        return np.asarray([idx // self.width, idx % self.width])

    def start(self, idx: int) -> None:
        # when opening first panel, you have to call start and specify which position you would like to open.
        non_neighbors = np.setdiff1d(
            np.arange(self.width * self.height), np.append(self._neighbors[idx], idx), assume_unique=True
        )
        mine_loc = self._rng.choice(non_neighbors, size=self._n_mines, replace=False)
        self._field[mine_loc] = -2

        for i in range(self.height * self.width):
            if self._field[i] == -2:
                continue

            self._field[i] = np.sum(self._field[self._neighbors[i]] == -2)

        self.open(idx)

    def open(self, idx: int) -> None:
        self.open_multiple(np.asarray([idx]))

    def open_multiple(self, indices: np.ndarray) -> None:
        self._cell_state[indices] = self._field[indices]
        if np.any(self._cell_state[indices] == -2):
            self._over = True

        self._open_around_zero(indices[self._cell_state[indices] == 0])
        n_close = np.count_nonzero(self._cell_state == CLOSED)
        if n_close == self._n_mines and not self._over:
            self._clear = True
        if not self._terminated:
            self.plot_field()

    def _open_around_zero(self, new_zero_indices: list[int]) -> None:
        q = deque(new_zero_indices)
        while len(q) > 0:
            idx = q.popleft()
            neighbor_indices = self._neighbors[idx]
            closed = self._cell_state[neighbor_indices] == CLOSED
            self._cell_state[neighbor_indices] = self._field[neighbor_indices]
            q.extend([i for i in neighbor_indices[closed] if self._cell_state[i] == 0])

    def plot_field(self) -> None:
        print(self._get_judge_statement())
        if not self._plot_field:
            return

        for y in range(self.height):
            s = " ".join([self._convert_string(y, x) for x in range(self.width)])
            print(s)
        print("")

    def _get_judge_statement(self) -> str:
        s = ""
        if self._over:
            self._terminated = True
            s = "*******************\n"
            s += "***  game over  ***\n"
            s += "*******************\n"
        elif self._clear:
            self._terminated = True
            s = "*******************\n"
            s += "*** game clear! ***\n"
            s += "*******************\n"

        return s

    def _convert_string(self, y: int, x: int) -> str:
        idx = self.loc2idx(y, x)
        if self._cell_state[idx] == CLOSED:
            return "x"
        elif self._field[idx] >= 0 and self._cell_state[idx] >= 0:
            return str(self._cell_state[idx])
        else:
            return "@"

    def _out_of_field(self, y: int, x: int) -> bool:
        return not (0 <= x < self.width and 0 <= y < self.height)
