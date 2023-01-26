import time

from src.mine_sweeper import Difficulties, MineSweeper
from src.player import Player


def solve(seed: int, n_games: int, difficulty: int) -> None:
    s = time.time()
    n_win, start = 0, seed

    for n in range(start, start + n_games):
        field = MineSweeper(difficulty, seed=n)
        n_win += Player(field).solve()
        print(f"{n + 1 - start}: winning {n_win}\n")

    print(f"winning rate: {100 * n_win / n_games:.3f} %")
    print(time.time() - s)


if __name__ == "__main__":
    """
    easy   949/1000
    normal 823/1000
    hard    42/100

    153/200
    155/200
    161/200
    168/200
    """
    solve(seed=0, n_games=200, difficulty=Difficulties.easy.value)
