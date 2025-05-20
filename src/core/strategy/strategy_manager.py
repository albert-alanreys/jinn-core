import ast
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.testing.tester import Tester


class StrategyManager:
    def __init__(
        self,
        data_to_format: dict,
        tester: Optional['Tester']
    ) -> None:
        self.data_to_format = data_to_format
        self.tester = tester

    def update_strategy(
        self,
        id: str,
        param_name: str,
        new_value: list | str
    ) -> None:
        try:
            params = self.data_to_format[id]['params']
            old_value = params[param_name]

            if isinstance(new_value, list):
                new_value = list(map(lambda x: float(x), new_value))
            else:
                new_value = ast.literal_eval(new_value.capitalize())

                if isinstance(old_value, float):
                    if isinstance(new_value, int):
                        new_value = float(new_value)

            if type(old_value) != type(new_value):
                raise ValueError()

            params[param_name] = new_value
            instance = self.data_to_format[id]['type'](
                client=self.data_to_format[id]['client'],
                all_params=params
                )
            self.data_to_format[id]['instance'] = instance

            if self.tester is not None:
                equity, metrics = self.tester.calculate_strategy(
                    self.data_to_format[id]
                )
                self.data_to_format[id]['equity'] = equity
                self.data_to_format[id]['metrics'] = metrics
            else:
                market_data = {
                    'market': self.data_to_format[id]['market'],
                    'symbol': self.data_to_format[id]['symbol'],
                    'klines': self.data_to_format[id]['klines'],
                    'p_precision':
                        self.data_to_format[id]['p_precision'],
                    'q_precision':
                        self.data_to_format[id]['q_precision'],
                }
                self.data_to_format[id]['instance'].start(market_data)
        except ValueError:
            raise ValueError()
        except KeyError:
            raise KeyError()