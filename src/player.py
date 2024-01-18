import numpy as np

from src.base_player import BasePlayer
from src.probability import ProbabilityCalculator


class Player(BasePlayer):
    def _open_by_proba(self) -> None:
        prob = ProbabilityCalculator(
            cell_state=self._field.cell_state,
            flags=self.flags,
            neighbors=self._field.neighbors,
            n_mines=self._field.n_mines,
        )
        target, p_land = prob.compute()
        safe_cell_exist = np.count_nonzero(target.proba == 0.0)

        if safe_cell_exist:
            self._flags[target.index[target.proba == 1.0]] = True
            self._open_multiple(target.index[target.proba == 0.0])
        elif target.proba.size != 0 and np.min(target.proba) < p_land:
            self._open(target.index[np.argmin(target.proba)])
        else:
            self._open_land()
