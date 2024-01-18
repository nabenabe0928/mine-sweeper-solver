import time
from argparse import ArgumentParser

from src.constants import Difficulties
from src.mine_sweeper import MineSweeper
from src.player import Player
from src.player_cpp import PlayerCpp


def solve(seed: int, n_games: int, difficulty: int, cpp: bool) -> None:
    s = time.time()
    n_win, start = 0, seed

    player_cls = PlayerCpp if cpp else Player
    for n in range(start, start + n_games):
        field = MineSweeper(difficulty, seed=n)
        n_win += player_cls(field).solve()
        print(f"{n + 1 - start}: winning {n_win}\n")

    print(f"winning rate: {100 * n_win / n_games:.3f} %")
    print(time.time() - s)


if __name__ == "__main__":
    """
    Easy   9602/10000
    Medium 1742/2000
    Hard    181/400
    """
    parser = ArgumentParser()
    parser.add_argument("--cpp", default="False", choices=["True", "False"])
    parser.add_argument("--diff", default="medium", choices=[d.name for d in Difficulties])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--N", type=int, default=100)

    args = parser.parse_args()
    solve(seed=args.seed, n_games=args.N, difficulty=getattr(Difficulties, args.diff).value, cpp=eval(args.cpp))
