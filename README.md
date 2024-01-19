# Probablity-based solver for MineSweeper

[![Buildl Status](https://github.com/nabenabe0928/mine-sweeper-solver/workflows/Python3.8/badge.svg?branch=main)](https://github.com/nabenabe0928/mine-sweeper-solver)
[![codecov](https://codecov.io/gh/nabenabe0928/mine-sweeper-solver/branch/main/graph/badge.svg?token=FQWPWEJSWE)](https://codecov.io/gh/nabenabe0928/mine-sweeper-solver)

This solver uses the depth-first search to compute the probabilities of each cell having a mine and I speeded up the code using NumPy and caching. There might be room for improvement in the speed, but my implementation achieves the theoretical performance bound.

<p align="middle">
    <img src="/demodata/medium18.gif" width="96%" />
</p>

## Requirements
- python 3.8
- numpy >= 1.21.5

## Performance
Here, I listed the winning rate in each difficulty.

|Difficulty | Win | Lose | Winning rate |
|:--:|:--:|:--:|:--:|
|Easy | 9598 | 402 | 96%|
|Medium | 8725 | 1275 | 87%|
|Hard | 460 | 540 | 46%|

Note that each difficulty has the following field:
- Easy: $9 \times 9$ with $10$ mines
- Medium: $16 \times 16$ with $40$ mines
- Hard: $16 \times 30$ with $100$ mines

In the experiments, seeds 132, 182, 188, 243, 268, and 273 in Hard did not finish in one hour, so I counted as lost.

## Reproduce the experiments

```shell
# Easy
python solve.py --diff easy --seed 0 --N 1000 --cpp False

# Medium
python solve.py --diff medium --seed 0 --N 1000 --cpp False

# Medium
python solve.py --diff hard --seed 0 --N 100 --cpp False
```

> [!NOTE]
> If you would like to use the C++ implementation, you need to build the C++ code and move it to your Python path.
> ```shell
> $ mkdir build
> $ cd build
> $ cmake ..
> $ make
> # For example, the path is under the site-packages/ directory of your Python.
> $ mv mine_sweeper_solver.* <path/to/your/python/lib>
> ```

Also, for the visualization demo, try the following command:

```shell
python validate_probability.py
```

## Demos with other seeds

<p align="middle">
    <img src="/demodata/medium11.gif" width="49%" />
    <img src="/demodata/medium14.gif" width="49%" />
</p>

<p align="middle">
    <img src="/demodata/hard00.gif" width="98%" />
</p>