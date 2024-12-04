import os
import json
import random
import multiprocessing as mp
from functools import partial

from src.model.api_clients.binance_client import BinanceClient
from src.model.api_clients.bybit_client import BybitClient
from src.model.strategies.registry import Registry


class Optimizer:
    iterations = 20_000
    population_size = 50
    max_population_size = 300

    number_of_starts = 1
    output_results = 2

    def __init__(self, optimization: dict[str, str]) -> None:
        self.strategies = dict()

        for strategy in Registry.data.values():
            file_path = os.path.abspath(
                f'src/model/strategies/{strategy.name}'
                f'/optimization/optimization.json'
            )

            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    
                    for i in data:
                        exchange = i['exchange'].lower()
                        symbol = i['symbol']
                        interval = i['interval']
                        datetime1 = i['date/time #1']
                        datetime2 = i['date/time #2']
                        datetime3 = i['date/time #3']

                        if exchange == 'binance':
                            interval = BinanceClient.intervals[interval]
                            client1 = BinanceClient()
                            client2 = BinanceClient()
                        elif exchange == 'bybit':
                            interval = BybitClient.intervals[interval]
                            client1 = BybitClient()
                            client2 = BybitClient()

                        client1.get_klines(
                            symbol, interval, datetime1, datetime2
                        )
                        client2.get_klines(
                            symbol, interval, datetime2, datetime3
                        )
                        self.strategies[
                            f'{strategy.name}_'
                            f'{exchange}_'
                            f'{symbol}_'
                            f'{interval} '
                            f'T{datetime1} - {datetime3}'
                        ] = {
                            'instance': strategy.type,
                            'client1': client1,
                            'client2': client2
                        }
            except FileNotFoundError:
                pass

        if len(self.strategies) == 0:
            strategy_name = Registry.data[optimization['strategy']].name
            strategy_type = Registry.data[optimization['strategy']].type
            exchange = optimization['exchange'].lower()
            symbol = optimization['symbol']
            interval = optimization['interval']
            datetime1 = optimization['date/time #1']
            datetime2 = optimization['date/time #2']
            datetime3 = optimization['date/time #3']

            if exchange == 'binance':
                interval = BinanceClient.intervals[interval]
                client1 = BinanceClient()
                client2 = BinanceClient()
            elif exchange == 'bybit':
                interval = BybitClient.intervals[interval]
                client1 = BybitClient()
                client2 = BybitClient()

            client1.get_klines(symbol, interval, datetime1, datetime2)
            client2.get_klines(symbol, interval, datetime2, datetime3)
            self.strategies[
                f'{strategy_name}_'
                f'{exchange}_'
                f'{symbol}_'
                f'{interval} '
                f'T{datetime1} - {datetime3}'
            ] = {
                'instance': strategy_type,
                'client1': client1,
                'client2': client2
            }

    def create(self) -> None:
        samples = [
            [               
                random.choice(j) 
                    for j in self.strategy.opt_parameters.values()
            ]
            for _ in range(Optimizer.population_size)
        ]
        self.population = {
            k: v for k, v in zip(
                map(
                    partial(self.fit, client=self.client1),
                    samples
                ),
                samples
            )
        }
        self.sample_length = len(self.strategy.opt_parameters)

    def fit(
        self,
        sample: list,
        client: BinanceClient | BybitClient
    ) -> float:
        strategy = self.strategy(opt_parameters=sample)
        strategy.start(client)
        score = round(
            strategy.completed_deals_log[8::13].sum() /
                strategy.initial_capital * 100,
            2
        )
        return score

    def select(self) -> None:
        if random.randint(0, 1) == 0:
            score = max(self.population)
            parent_1 = self.population[score]
            population_copy = self.population.copy()
            population_copy.pop(score)
            parent_2 = random.choice(list(population_copy.values()))
            self.parents = [parent_1, parent_2]
        else:
            parents = random.sample(list(self.population.values()), 2)
            self.parents = [parents[0], parents[1]]

    def recombine(self) -> None:
        r_number = random.randint(0, 1)

        if r_number == 0:
            delimiter = random.randint(1, self.sample_length - 1)
            self.child = (self.parents[0][:delimiter] 
                        + self.parents[1][delimiter:])
        else:
            delimiter_1 = random.randint(1, self.sample_length // 2 - 1)
            delimiter_2 = random.randint(
                self.sample_length // 2 + 1, self.sample_length - 1)
            self.child = (self.parents[0][:delimiter_1]
                        + self.parents[1][delimiter_1:delimiter_2]
                        + self.parents[0][delimiter_2:])

    def mutate(self) -> None:
        if random.randint(1, 100) <= 95:
            gene_num = random.randint(0, self.sample_length - 1)
            gene_value = random.choice(
                list(self.strategy.opt_parameters.values())[gene_num]
            )
            self.child[gene_num] = gene_value
        else:
            for i in range(len(self.child)):
                self.child[i] = random.choice(
                    list(self.strategy.opt_parameters.values())[i]
                )

    def expand(self) -> None:
        self.population[self.fit(self.child, self.client1)] = self.child

    def kill(self) -> None:
        while len(self.population) > Optimizer.max_population_size:
            self.population.pop(min(self.population))

    def elect(self) -> dict[float, list]:
        best_samples = dict()

        for _ in range(Optimizer.output_results):
            try:
                best_score = max(self.population)
                best_samples[best_score] = self.population[best_score]
                self.population.pop(best_score)
            except Exception:
                break

        return best_samples

    def validate(self) -> None:
        validation_population = {
            k: v for k, v in zip(
                map(
                    partial(self.fit, client=self.client2),
                    self.population.values()
                ),
                self.population.items()
            )
        }
        population_size = int(len(self.population) * 0.25)
        self.population.clear()

        for _ in range(population_size):
            try:
                best_score = max(validation_population)
                old_score = validation_population[best_score][0]
                sample = validation_population[best_score][1]
                self.population[old_score] = sample
                validation_population.pop(best_score)
            except Exception:
                break

    def write(
        self,
        strategy: tuple[str, dict],
        best_samples: dict[float, list]
    ) -> None:
        strategy_name = strategy[0][
            : strategy[0].rfind(
                '_', 0, strategy[0].rfind(
                    '_', 0, strategy[0].rfind('_') - 1
                ) - 1
            )
        ]
        file_name = strategy[0][
            : strategy[0].rfind('T') - 1
        ].lstrip(strategy_name)
        time = strategy[0][strategy[0].rfind('T') + 1 : ]
        file_path = os.path.abspath(
            f'src/model/strategies/{strategy_name}'
            f'/optimization/{file_name}.txt'
        )

        for score, sample in best_samples.items():
            file_text = (
                f'Period: {time}\nNet profit, %: {score}\n{'=' * 50}\n'
            )
            file_text += ''.join(
                [
                    f'{value} = {sample[index]}\n'
                        for index, value in enumerate(
                            strategy[1]['instance'].opt_parameters.keys()
                        )
                ]
            )
            file_text += ''.join('=' * 50)
            file_text += '\n\n'

            with open(file_path, 'a') as file:
                print(file_text, file=file)

    def optimize(
        self,
        strategy: tuple[str, dict]
    ) -> dict[float, list]:
        best_samples = {}

        for i in range(Optimizer.number_of_starts):
            self.client1 = strategy[1]['client1']
            self.client2 = strategy[1]['client2']
            self.strategy = strategy[1]['instance']
            self.create()

            for j in range(1, Optimizer.iterations + 1):
                self.select()
                self.recombine()
                self.mutate()
                self.expand()
                self.kill()

                if j % 1000 == 0:
                    self.validate()

            best_samples.update(self.elect())
            strategy_name = strategy[0][
                : strategy[0].find(' ')
            ]
            print(f'Оптимизация #{i + 1} для {strategy_name} завершена.')

        return best_samples

    def start(self) -> None:
        print('Выполняется оптимизация.')

        with mp.Pool(mp.cpu_count()) as pool:
            result = zip(
                self.strategies.items(),
                pool.map(
                    self.optimize, self.strategies.items()
                )
            )

        for strategy, best_samples in result:
            self.write(strategy, best_samples)