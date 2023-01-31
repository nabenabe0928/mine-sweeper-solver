import pytest
import unittest

import numpy as np

from src.mine_sweeper import MineSweeper


class TestMineSweeper(unittest.TestCase):
    def test_field(self) -> None:
        for i in [0, 1, 2]:
            w, h = [9, 16, 30][i], [9, 16, 16][i]
            field = MineSweeper(difficulty=i)
            assert field._field.size == w * h
            assert field.cell_state.size == w * h
            assert field.width == w
            assert field.height == h
            assert field.n_mines == [10, 40, 100][i]
            assert not field.over and not field.clear
            assert id(field.cell_state) != id(field._cell_state)

    def test_loc2idx(self) -> None:
        field = MineSweeper(difficulty=2)
        for i in range(field.height * field.width):
            vals = field.idx2loc(i)
            assert vals[0] == i // field.width
            assert vals[1] == i % field.width

        with pytest.raises(ValueError):
            field.idx2loc(480)

    def test_idx2loc(self) -> None:
        field = MineSweeper(difficulty=2)
        for i in range(field.height * field.width):
            val = field.loc2idx(i // field.width, i % field.width)
            assert val == i

        with pytest.raises(ValueError):
            field.idx2loc(np.array([30, 16]))

    def test_get_judge_statement(self) -> None:
        field = MineSweeper(difficulty=2)
        val = field._get_judge_statement()
        assert val == ""

        field._clear = True
        val = field._get_judge_statement()
        assert "clear" in val

        field._over = True
        val = field._get_judge_statement()
        assert "over" in val


if __name__ == "__main__":
    unittest.main()
