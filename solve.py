import time
from argparse import ArgumentParser

from src.constants import Difficulties
from src.mine_sweeper import MineSweeper
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
    easy   974/1000
    normal 870/1000
    hard    48/98
    """
    parser = ArgumentParser()
    parser.add_argument("--diff", default="medium", choices=[d.name for d in Difficulties])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--N", type=int, default=100)

    args = parser.parse_args()
    solve(seed=args.seed, n_games=args.N, difficulty=getattr(Difficulties, args.diff).value)
