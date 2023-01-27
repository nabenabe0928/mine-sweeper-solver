import numpy as np

from src.probability import ProbabilityCalculator
from src.mine_sweeper import MineSweeper


"""
Validate the probability calculation by the following example.
      a b c d e f g h i j k l m n o p
     _________________________________
  0 | x x x x x x x x x x x x x x x x |  15
 16 | x x x x x x x x x x x x x x x x |  31
 32 | x x x x x x x x x x x x x x x x |  47
 48 | x x x x x x x x x x x x x x x x |  63
 64 | x x x x Q Q Q Q Q B Q Q A x x x |  79
 80 | x x x x Q 3 @ @ 3 2 2 2 @ Q x x |  95
 96 | x x x x B 3 2 2 1 0 0 1 2 Q x x | 111
112 | x x x x Q 2 0 0 0 0 1 1 2 Q x x | 127
128 | x x x Q Q 2 1 0 0 0 1 @ 2 Q x x | 143
144 | x x x Q 2 @ 2 1 1 1 2 3 A Q x x | 159
160 | x x x Q 2 Q 2 Q Q 1 Q Q B x x x | 175
176 | x x x Q Q 1 2 A A 1 1 2 A x x x | 191
192 | x x x x Q A A B 1 1 1 1 A x x x | 207
208 | x x x x x x A A 2 2 B A A x x x | 223
224 | x x x x x x Q 1 Q Q A x x x x x | 239
240 | x x x x x x Q 1 Q x x x x x x x | 255
     ---------------------------------
where each symbol means:
    - x: a closed cell
    - Q: a closed cell and unsure if it has a mine or not.
    - A: a closed cell, but sure that it has no mine.
    - B: a closed cell, but sure that it has a mine.
    - @: a flag.
    - 1--8: the number of mines in its neighbors.

The indices of A: [ 76 156 183 184 188 197 198 204 214 215 219 220 234]
The indices of B: [ 73 100 172 199 218]
"""

ms = MineSweeper(difficulty=1)
cell_state = np.array(
    [
        [-1] * 16,
        [-1] * 16,
        [-1] * 16,
        [-1] * 16,
        [-1] * 16,
        [-1, -1, -1, -1, -1, 3, -1, -1, 3, 2, 2, 2, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, 3, 2, 2, 1, 0, 0, 1, 2, -1, -1, -1],
        [-1, -1, -1, -1, -1, 2, 0, 0, 0, 0, 1, 1, 2, -1, -1, -1],
        [-1, -1, -1, -1, -1, 2, 1, 0, 0, 0, 1, -1, 2, -1, -1, -1],
        [-1, -1, -1, -1, 2, -1, 2, 1, 1, 1, 2, 3, -1, -1, -1, -1],
        [-1, -1, -1, -1, 2, -1, 2, -1, -1, 1, -1, -1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, 1, 2, -1, -1, 1, 1, 2, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, -1, 2, 2, -1, -1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, 1, -1, -1, -1, -1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, 1, -1, -1, -1, -1, -1, -1, -1, -1],
    ]
).flatten()
flags = np.zeros_like(cell_state, dtype=np.bool8)
flags[[86, 87, 92, 139, 149]] = True
prob = ProbabilityCalculator(
    cell_state=cell_state,
    flags=flags,
    neighbors=ms.neighbors,
    n_mines=ms.n_mines,
)

target = prob.compute()[0]
print(target.index[target.proba == 0])
print(target.index[target.proba == 1])
