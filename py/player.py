from copy import deepcopy
from typing import Tuple

import numpy as np

from mine_sweeper import MineSweeper
from probability import ProbabilityCalculator


class Player:
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
        self._n_open = 0
        self._neighbors = self._field.neighbors
        self._flags = np.zeros(self._W * self._H, dtype=np.bool8)
        self._n_cells = field.width * field.height

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

    def start(self, y: int, x: int) -> None:
        self._field.start(y, x)

    def idx2loc(self, idx: int) -> Tuple[int, int]:
        return self._field.idx2loc(idx)

    def add_flag(self, idx: int) -> None:
        self._flags[idx] = True

    def open(self, idx: int) -> None:
        y, x = self.idx2loc(idx)
        self._field.open(y, x)

    def build_flag(self) -> None:
        cell_state = self._field.cell_state
        cell_opened = (cell_state != -1)
        target_indices = np.arange(self._n_cells)[cell_state > 0]
        for idx in target_indices:
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

    def opened_any(self) -> bool:
        cell_state = self._field.cell_state
        n_open = np.count_nonzero(cell_state >= 0)
        if n_open != self._n_open:
            self._n_open = n_open
            return True
        else:
            return False

    def open_land(self) -> None:
        cell_state = self._field.cell_state
        cell_closed = (cell_state == -1)
        closed_indices = np.arange(self._n_cells)[cell_closed]
        for idx in closed_indices:
            neighbor_indices = self._neighbors[idx]
            n_closed = np.count_nonzero(cell_closed[neighbor_indices])
            if n_closed == neighbor_indices.size:
                y, x = self.idx2loc(idx)
                self._field.open(y, x)
                return


def main(field: MineSweeper) -> bool:
    player = Player(field)
    player.start(player.H // 2, player.W // 2)

    while not player.over and not player.clear:
        player.build_flag()
        player.open_safe_cells()
        if not player.opened_any():
            prob = ProbabilityCalculator(field=field, flags=player.flags)
            target, p_land = prob.compute()
            surely_no_mine_indices = target.index[target.proba == 0.0]
            if surely_no_mine_indices.size > 0:
                for idx, p in zip(target.index, target.proba):
                    if p == 0:
                        player.open(idx)
                    elif p == 1:
                        player.add_flag(idx)
            elif target.proba.size != 0 and np.min(target.proba) < p_land:
                player.open(target.index[np.argmin(target.proba)])
            else:
                player.open_land()

    return player.clear


if __name__ == "__main__":
    """
    easy   950/1000
    normal 823/1000
    hard    42/100
    """
    import time

    s = time.time()
    n_win = 0
    n_games = 1000
    difficulty = 0

    for n in range(n_games):
        field = MineSweeper(difficulty, seed=n)
        n_win += main(field)
        print(f"{n + 1}: winning {n_win}\n")

    print(f"winning rate: {100 * n_win / n_games:.3f} %")
    print(time.time() - s)