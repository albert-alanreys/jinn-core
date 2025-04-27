import numpy as np


def get_random_percentages(quantity: int, min: int, step: int) -> list:
    sample = np.concatenate(
        (
            np.random.choice(
                range(min, 100, step), quantity - 1, False
            ),
            (0, 100)
        )
    )
    sample.sort()
    sample1 = np.concatenate((sample, np.full(1, 0)))
    sample2 = np.concatenate((np.full(1, 0), sample))
    values = (sample1 - sample2)[1:-1].astype(float).tolist()
    return values