from typing import Dict, Tuple, Type

from src import DickeyFullerV1
from src import DevourerV3
from src import NuggetV2
from src import NuggetV4
from src import NuggetV5


class Strategies:
    registry: Dict[str, Tuple[str, Type]] = {
        'devourer_v3': ('devourer_v3', DevourerV3),
        'dickey_fuller_v1': ('dickey_fuller_v1', DickeyFullerV1),
        'nugget_v2': ('nugget_v2', NuggetV2),
        'nugget_v4': ('nugget_v4', NuggetV4),
        'nugget_v5': ('nugget_v5', NuggetV5)
    }