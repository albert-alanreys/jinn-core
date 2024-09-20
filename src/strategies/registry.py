from collections import namedtuple

from src import DickeyFullerV1
from src import DevourerV3
from src import NuggetV2
from src import NuggetV4
from src import NuggetV5

Strategy = namedtuple('Strategy', ['name', 'type'])


class Registry:
    data = {
        'devourer_v3': Strategy('devourer_v3', DevourerV3),
        'dickey_fuller_v1': Strategy('dickey_fuller_v1', DickeyFullerV1),
        'nugget_v2': Strategy('nugget_v2', NuggetV2),
        'nugget_v4': Strategy('nugget_v4', NuggetV4),
        'nugget_v5': Strategy('nugget_v5', NuggetV5)
    }