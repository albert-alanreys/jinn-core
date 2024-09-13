import numpy as np

def random_trading_volumes(quantity, min_volume, step):
    sample = np.concatenate(
        (
            np.random.choice(
                range(min_volume, 100, step), quantity - 1, False
            ),
            (0, 100)
        )
    )
    sample.sort()
    sample1 = np.concatenate((sample, np.full(1, 0)))
    sample2 = np.concatenate((np.full(1, 0), sample))
    values = (sample1 - sample2)[1:-1].astype(float).tolist()
    return values