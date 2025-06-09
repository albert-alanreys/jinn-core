import ast
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.testing.tester import Tester


class StrategyManager:
    def __init__(
        self,
        strategy_contexts: dict,
        tester: Optional['Tester']
    ) -> None:
        self.strategy_contexts = strategy_contexts
        self.tester = tester

    def update_strategy(
        self,
        context_id: str,
        param_name: str,
        new_value: list | str
    ) -> None:
        try:
            params = self.strategy_contexts[context_id]['instance'].params
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
            strategy_instance = self.strategy_contexts[context_id]['type'](
                client=self.strategy_contexts[context_id]['client'],
                all_params=params
                )
            self.strategy_contexts[context_id]['instance'] = strategy_instance

            if self.tester is not None:
                equity, metrics = self.tester.calculate_strategy(
                    self.strategy_contexts[context_id]
                )
                self.strategy_contexts[context_id]['equity'] = equity
                self.strategy_contexts[context_id]['metrics'] = metrics
            else:
                self.strategy_contexts[context_id]['instance'].start(
                    self.strategy_contexts[context_id]['market_data']
                )
        except ValueError:
            raise ValueError()
        except KeyError:
            raise KeyError()