import numpy as np

from src.base_player import BasePlayer

import mine_sweeper_solver


class PlayerCpp(BasePlayer):
    def _open_by_proba(self) -> None:
        probs = np.asarray(
            mine_sweeper_solver.calculate_probability(
                self._field.cell_state.reshape(self.H, self.W).tolist(), self._field.n_mines
            )
        ).flatten()
        closed_mask = self._field.cell_state == -1
        safe_mask = probs[closed_mask] == 0.0
        closed_indices = np.arange(probs.size)[closed_mask]
        if np.any(safe_mask):
            self._flags[closed_indices[probs[closed_indices] == 1.0]] = True
            self._open_multiple(closed_indices[safe_mask])
        else:
            self._open(closed_indices[np.argmin(probs[closed_indices])])
