import os
from typing import Optional

import matplotlib.pyplot as plt

import numpy as np

from src.probability import ProbabilityCalculator
from src.mine_sweeper import MineSweeper


def visualize(cell_state: np.ndarray, flags: np.ndarray, identifier: Optional[int] = None) -> None:
    size = cell_state.size
    difficulty = {81: 0, 256: 1, 480: 2}[size]
    ms = MineSweeper(difficulty=difficulty)

    prob = ProbabilityCalculator(
        cell_state=cell_state,
        flags=flags,
        neighbors=ms.neighbors,
        n_mines=ms.n_mines,
    )
    target = prob.compute()[0]

    W, H = ms.width, ms.height

    _, ax = plt.subplots(figsize=(10, 10))
    ax.tick_params(labelbottom=False, bottom=False, labelleft=False, left=False)
    ax.vlines(np.arange(W + 1), 0, H, colors="black")
    ax.hlines(np.arange(H + 1), 0, W, colors="black")
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)

    COLORS_OF_NUMBERS = ["white", "blue", "green", "red", "purple", "black", "gray", "darkred", "cyan"]

    for idx, (state, flag) in enumerate(zip(cell_state, flags)):
        y, x = idx // W, idx % W
        if state == -1:
            ax.fill_between([x, x + 1], H - y - 1, H - y, color="cyan")
            if flag:
                kwargs = dict(color="orange", ha="center", va="center", weight="bold")
                ax.text(x + 0.5, H - y - 0.5, "P", fontsize=15, **kwargs)
        else:
            color = COLORS_OF_NUMBERS[state]
            ax.text(x + 0.5, H - y - 0.5, f"{state}", color=color, ha="center", va="center")

    for idx, prob in zip(target.index, target.proba):
        y, x = idx // W, idx % W
        ax.text(x + 0.5, H - y - 0.5, f"{int(prob*100)}", ha="center", va="center")

    ax.set_xlabel("NOTE: the numbers in cyan cells show the percentage of having a mine.", fontsize=16)
    os.makedirs("demodata", exist_ok=True)

    if identifier is not None:
        plt.savefig(f"demodata/demo{identifier:0>3}.png", bbox_inches="tight")
    else:
        plt.show()
