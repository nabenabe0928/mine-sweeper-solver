import unittest

from src.mine_sweeper import MineSweeper
from src.player import Player


def test_player():
    for i in range(100):
        field = MineSweeper(difficulty=0)
        Player(field).solve()

    for i in range(3):
        field = MineSweeper(difficulty=1)
        Player(field).solve()


if __name__ == "__main__":
    unittest.main()
