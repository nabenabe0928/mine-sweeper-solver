from MineSweeper import MineSweeper
from probability import probability
import math
import numpy as np


class _game():
    def __init__(self, player):
        self.player = player
        self.W = player.width
        self.H = player.height
        self.flag = [[False for h in range(self.H)] for w in range(self.W)]
        self.n_open = self.W * self.H

    def GetFlag(self):
        for w in range(self.W):
            for h in range(self.H):
                if self.player.GetCellInfo(w, h) != -1:
                    count = 0
                    around = self.player.around(w, h)
                    for a in around:
                        if self.player.GetCellInfo(a[0], a[1]) == -1:
                            count += 1

                    if count == self.player.GetCellInfo(w, h):
                        for a in around:
                            if self.player.GetCellInfo(a[0], a[1]) == -1:
                                self.flag[a[0]][a[1]] = True

    def OpenSafe(self):
        for w in range(self.W):
            for h in range(self.H):
                if self.player.GetCellInfo(w, h) != -1:
                    count = 0
                    around = self.player.around(w, h)
                    for a in around:
                        if self.flag[a[0]][a[1]]:
                            count += 1

                    if count == self.player.GetCellInfo(w, h):
                        for a in around:
                            if not self.flag[a[0]][a[1]] and self.player.GetCellInfo(a[0], a[1]) == -1:
                                self.player.open(a[0], a[1])

    def cannot_open(self):
        n_open = 0
        for w in range(self.W):
            for h in range(self.H):
                if self.player.GetCellInfo(w, h) >= 0:
                    n_open += 1

        if n_open == self.n_open:
            return True
        else:
            self.n_open = n_open
            return False

    def num_to_position(self, num):
        h = math.floor(num / self.W)
        w = num - (self.W * h)
        return [w, h]

    def open_land(self):
        for w in range(self.W):
            for h in range(self.H):
                if self.player.GetCellInfo(w, h) == -1:
                    land = True
                    around = self.player.around(w, h)
                    for a in around:
                        if self.player.GetCellInfo(a[0], a[1]) != -1:
                            land = False
                    if land:
                        self.player.open(w, h)
                        return None


def main(player):
    game = _game(player)
    game.player.start(int(game.W / 2), int(game.H / 2))
    game.GetFlag()
    game.OpenSafe()

    while not game.player.over and not game.player.clear:
        game.GetFlag()
        game.OpenSafe()

        if game.cannot_open():
            prob = probability(game.player, game.flag)
            target, p_land = prob.searching()
            print(target, p_land)

            if 0 in target[2]:
                for i, tar in enumerate(target[2]):
                    if tar == 0:
                        position = game.num_to_position(target[0][i])
                        game.player.open(position[0], position[1])
                    elif tar == 1:
                        position = game.num_to_position(target[0][i])
                        game.flag[position[0]][position[1]] = True

            elif len(target[2]) != 0 and min(target[2]) < p_land:
                position = game.num_to_position(target[0][np.argmin(target[2])])
                game.player.open(position[0], position[1])
            else:
                game.open_land()

    return game.player.clear


if __name__ == "__main__":
    """
    easy   950/1000
    normal 823/1000
    hard    42/100
    """
    n_win = 0
    n_game = 100
    difficulty = 0
    import time
    s = time.time()

    for n in range(n_game):
        player = MineSweeper(difficulty)
        n_win += main(player)
        print("{}: winning {}".format(n + 1, n_win))
        print("")

    print("winning rate: {:.3f} %".format(100 * float(n_win) / float(n_game)))
    print(time.time() - s)
