import ast

from src.core.enums import Mode


class StrategyManager:
    def __init__(self, mode: str, data_to_format: dict) -> None:
        self.mode = mode
        self.data_to_format = data_to_format[1]

        if self.mode is Mode.TESTING:
            self.tester = data_to_format[0]

    def update_strategy(
        self,
        strategy_id: str,
        param_name: str,
        new_value: int | float
    ) -> None:
        try:
            parameters = self.data_to_format[strategy_id]['parameters']
            old_value = parameters[param_name]

            if isinstance(new_value, list):
                new_value = list(map(lambda x: float(x), new_value))
            else:
                new_value = ast.literal_eval(new_value.capitalize())

                if isinstance(old_value, float):
                    if isinstance(new_value, int):
                        new_value = float(new_value)

            if type(old_value) != type(new_value):
                raise ValueError()

            parameters[param_name] = new_value
            instance = (
                self.data_to_format[strategy_id]['type'](
                    all_params=list(parameters.values())
                )
            )
            self.data_to_format[strategy_id]['instance'] = instance

            if self.mode is Mode.TESTING:
                equity, metrics = self.tester.calculate_strategy(
                    self.data_to_format[strategy_id]
                )
                self.data_to_format[strategy_id]['equity'] = equity
                self.data_to_format[strategy_id]['metrics'] = metrics
            else:
                self.data_to_format[strategy_id]['instance'].start(
                    {
                        'client': self.data_to_format[strategy_id]['client'],
                        'klines': self.data_to_format[strategy_id]['klines'],
                        'p_precision':
                            self.data_to_format[strategy_id]['p_precision'],
                        'q_precision':
                            self.data_to_format[strategy_id]['q_precision'],
                    }
                )
        except ValueError:
            raise ValueError()
        except KeyError:
            raise KeyError()