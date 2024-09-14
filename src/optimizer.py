from functools import partial
import multiprocessing as mp
import random
import json
import os


class Optimizer:
    iterations = 25000
    population_size = 50
    max_population_size = 300

    number_of_starts = 1
    output_results = 2

    def __init__(self, optimization, http_clients, strategies):
        self.http_clients_and_strategies = dict()

        for strategy in strategies.values():
            file_path = os.path.abspath(
                'src/strategies/' + strategy['name'] +
                '/optimization/optimization.json'
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
                            http_client1 = http_clients[0]()
                            http_client2 = http_clients[0]()
                        elif exchange == 'bybit':
                            http_client1 = http_clients[1]()
                            http_client2 = http_clients[1]()

                        http_client1.get_data(
                            symbol, interval, datetime1, datetime2
                        )
                        http_client2.get_data(
                            symbol, interval, datetime2, datetime3
                        )
                        self.http_clients_and_strategies[
                            f'{strategy['name']}_'
                            f'{exchange}_'
                            f'{symbol}_'
                            f'{interval} '
                            f'T{datetime1} - {datetime3}'
                        ] = {
                            'http_client1': http_client1,
                            'http_client2': http_client2,
                            'strategy': strategy['class']
                        }
            except Exception:
                pass

        if len(self.http_clients_and_strategies) == 0:
            strategy_name = strategies[optimization['strategy']]['name']
            strategy_class = strategies[optimization['strategy']]['class']
            exchange = optimization['exchange'].lower()
            symbol = optimization['symbol']
            interval = optimization['interval']
            datetime1 = optimization['date/time #1']
            datetime2 = optimization['date/time #2']
            datetime3 = optimization['date/time #3']

            if exchange == 'binance':
                http_client1 = http_clients[0]()
                http_client2 = http_clients[0]()
            elif exchange == 'bybit':
                http_client1 = http_clients[1]()
                http_client2 = http_clients[1]()

            http_client1.get_data(symbol, interval, datetime1, datetime2)
            http_client2.get_data(symbol, interval, datetime2, datetime3)
            self.http_clients_and_strategies[
                f'{strategy_name}_'
                f'{exchange}_'
                f'{symbol}_'
                f'{interval} '
                f'T{datetime1} - {datetime3}'
            ] = {
                'http_client1': http_client1,
                'http_client2': http_client2,
                'strategy': strategy_class
            }

    def create(self):
        samples = [
            [               
                random.choice(j) 
                    for j in self.strategy.opt_parameters.values()
            ]
            for _ in range(self.population_size)
        ]
        self.population = {
            k: v for k, v in zip(
                map(
                    partial(self.fit, http_client=self.http_client1),
                    samples
                ),
                samples
            )
        }
        self.sample_length = len(self.strategy.opt_parameters)

    def fit(self, sample, http_client):
        strategy = self.strategy(http_client, opt_parameters=sample)
        strategy.start()
        score = round(
            strategy.completed_deals_log[8::13].sum() /
                strategy.initial_capital * 100,
            2
        )
        return score

    def select(self):
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

    def recombine(self):
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

    def mutate(self):
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

    def expand(self):
        self.population[self.fit(self.child, self.http_client1)] = self.child

    def kill(self):
        while len(self.population) > self.max_population_size:
            self.population.pop(min(self.population))

    def elect(self):
        best_samples = dict()

        for _ in range(self.output_results):
            try:
                best_score = max(self.population)
                best_samples[best_score] = self.population[best_score]
                self.population.pop(best_score)
            except Exception:
                break

        return best_samples

    def validate(self):
        validation_population = {
            k: v for k, v in zip(
                map(
                    partial(self.fit, http_client=self.http_client2),
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

    def write(self, strategy, best_samples):
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
            'src/strategies/{}/optimization/{}.txt'.format(
                strategy_name, file_name
            )
        )

        for score, sample in best_samples.items():
            file_text = (
                'Period: ' + time + '\nNet profit, %: ' +
                str(score) + '\n' + ('=' * 50) + '\n'
            )
            file_text += ''.join(
                [
                    value + ' = ' + str(sample[count]) + '\n'
                        for count, value in enumerate(
                            strategy[1]['strategy'].opt_parameters.keys()
                        )
                ]
            )
            file_text += ''.join('=' * 50)
            file_text += '\n\n'

            with open(file_path, 'a') as file:
                print(file_text, file=file)

    def optimize(self, http_client_and_strategy):
        best_samples = {}

        for i in range(self.number_of_starts):
            self.http_client1 = http_client_and_strategy[1]['http_client1']
            self.http_client2 = http_client_and_strategy[1]['http_client2']
            self.strategy = http_client_and_strategy[1]['strategy']
            self.create()

            for j in range(1, self.iterations + 1):
                self.select()
                self.recombine()
                self.mutate()
                self.expand()
                self.kill()

                if j % 1000 == 0:
                    self.validate()

            best_samples.update(self.elect())
            strategy_name = http_client_and_strategy[0][
                : http_client_and_strategy[0].find(' ')
            ]
            print(f'Оптимизация #{i + 1} для {strategy_name} завершена.')

        return best_samples

    def start(self):
        with mp.Pool(mp.cpu_count()) as pool:
            strategies_and_best_samples = zip(
                self.http_clients_and_strategies.items(),
                pool.map(
                    self.optimize, self.http_clients_and_strategies.items()
                )
            )

        for strategy, best_samples in strategies_and_best_samples:
            self.write(strategy, best_samples)