from collections import namedtuple

from src.model.strategies import DickeyFullerV1
from src.model.strategies import DevourerV3
from src.model.strategies import NuggetV2
from src.model.strategies import NuggetV4
from src.model.strategies import NuggetV5

Strategy = namedtuple('Strategy', ['name', 'type'])


class Registry:
    data = {
        'devourer_v3': Strategy('devourer_v3', DevourerV3),
        'dickey_fuller_v1': Strategy('dickey_fuller_v1', DickeyFullerV1),
        'nugget_v2': Strategy('nugget_v2', NuggetV2),
        'nugget_v4': Strategy('nugget_v4', NuggetV4),
        'nugget_v5': Strategy('nugget_v5', NuggetV5)
    }