# MineSweeper

## Requirements
- python 3.8
- numpy >= 1.21.5

## Performance
Here, I listed the winning rate in each difficulty.

|Difficulty | Win | Lose | Winning rate |
|:--:|:--:|:--:|:--:|
|Easy ($9 \times 9$ with $10$ mines) | 974 | 26 | 97.4%|
|Medium ($16 \times 16$ with $40$ mines) | 870 | 130 | 87.0%|
|Hard ($16 \times 30$ with $100$ mines) | 49 | 51 | 49.0%|

## Reproduce the experiments

```shell
# Easy
python solve.py --diff easy --seed 0 --N 1000

# Medium
python solve.py --diff medium --seed 0 --N 1000

# Medium
python solve.py --diff hard --seed 0 --N 100
```
