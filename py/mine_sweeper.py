from typing import Literal, Optional

import numpy as np


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
        seed (Optional[int]):
            The random seed.
    """
    def __init__(self, difficulty: Literal[0, 1, 2] = 0, seed: Optional[int] = None):
        """
        Attributes:
            width (int):
                The width of the field.
            height (int):
                The height of the field.
            n_mines (int):
                The number of mines in the field.
            field (List[List[int]]):
                The ground truth of each cell.
                    0: No mines around this cell.
                    1--8: The corresponding number of mines exist around this cell.
        """
        self._rng = np.random.RandomState(seed)
        self._width = [9, 16, 30][difficulty]
        self._height = [9, 16, 16][difficulty]
        self._n_mines = [10, 40, 100][difficulty]
        self._field = [[0 for w in range(self.width)] for h in range(self.height)]
        self.cell = [[-1 for w in range(self.width)] for h in range(self.height)]
        self.zero = [[False for w in range(self.width)] for h in range(self.height)]
        self._over = False
        self._clear = False

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def over(self) -> bool:
        return self._over

    @property
    def clear(self) -> bool:
        return self._clear

    def start(self, x, y):
        # when opening first panel, you have to call start and specify which position you would like to open.
        ard = self.around(x, y)
        # first, get the array filled with rondom number whose size is same as the field itself.
        place_bomb = self._rng.random(size=self.width * self.height)
        # order the random number in the array and just get the arguments of this array.
        order = np.argsort(place_bomb)
        bomb_place = []

        b = 0
        t = 0
        while b < self._n_mines:
            """
            get the (t + 1)-th minimum random number in the place_bomb array
            if the position of order[t] is corresponds to the panel where you firstly choose at start,
            then you will remove the t from the bomb candidates and see next candidates.
            """
            bomb_candidate = self.num_to_position(order[t])

            if bomb_candidate not in ard and bomb_candidate != [x, y]:
                self._field[bomb_candidate[1]][bomb_candidate[0]] = -2
                b += 1
                bomb_place.append(bomb_candidate)

            t += 1

        for h in range(self.height):
            for w in range(self.width):
                position = [w, h]
                if position in bomb_place:
                    continue
                p = self.around(w, h)
                count = 0

                for pi in p:
                    if self._field[pi[1]][pi[0]] == -2:
                        count += 1
                self._field[h][w] = count
        self.open(x, y)

    def count(self, array, value):
        count = 0
        for h in range(self.height):
            for w in range(self.width):
                if array[h][w] == value:
                    count += 1
        return count

    def num_to_position(self, num):
        h = num // self.width
        w = num % self.width
        return [w, h]

    def out_of_field(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        else:
            return False

    def around(self, x, y):
        ard = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
        p = [[x + a[0], y + a[1]] for a in ard]

        for i in range(len(p) - 1, -1, -1):
            if self.out_of_field(p[i][0], p[i][1]):
                del p[i]
        return p

    def open(self, x, y):
        self.cell[y][x] = self._field[y][x]
        if self.cell[y][x] == -2:
            self._over = True
        while self.count(self.zero, True) != self.count(self.cell, 0):
            self.open_around_zero()
        count = 0

        for h in range(self.height):
            for w in range(self.width):
                if self.cell[h][w] == -1:
                    count += 1

        if count == self._n_mines and not self._over:
            self._clear = True
        self.plot_field()

    def open_around_zero(self):
        for h in range(self.height):
            for w in range(self.width):
                if self.cell[h][w] == 0:
                    self.zero[h][w] = True
                    around = self.around(w, h)
                    for a in around:
                        self.cell[a[1]][a[0]] = self._field[a[1]][a[0]]

    def GetCellInfo(self, x, y):
        return self.cell[y][x]

    def _convert_string(self, y: int, x: int) -> str:
        if self.cell[y][x] == -1:
            return "x"
        elif self._field[y][x] >= 0 and self.cell[y][x] >= 0:
            return str(self.cell[y][x])
        else:
            return "@"

    def plot_field(self):
        self.print_judge()
        for y in range(self.height):
            s = " ".join([self._convert_string(y, x) for x in range(self.width)])
            print(s)
        print("")

    def print_judge(self) -> None:
        if self._over:
            print("*******************")
            print("***  game over  ***")
            print("*******************")
            print("")
        elif self._clear:
            print("*******************")
            print("*** game clear! ***")
            print("*******************")
            print("")
