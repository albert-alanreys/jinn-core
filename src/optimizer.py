from functools import partial
import multiprocessing as mp
import random as r
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
                        exchange = i['exchange']
                        symbol = i['symbol']
                        interval = i['interval']
                        datetime1 = i['date/time #1']
                        datetime2 = i['date/time #2']
                        datetime3 = i['date/time #3']
                        datetime4 = i['date/time #4']

                        if exchange.lower() == 'binance':
                            http_client1 = http_clients[0]()
                            http_client2 = http_clients[0]()
                            http_client3 = http_clients[0]()
                        elif exchange.lower() == 'bybit':
                            http_client1 = http_clients[1]()
                            http_client2 = http_clients[1]()
                            http_client3 = http_clients[1]()

                        http_client1.get_data(
                            symbol, interval, datetime1, datetime2
                        )
                        http_client2.get_data(
                            symbol, interval, datetime2, datetime3
                        )
                        http_client3.get_data(
                            symbol, interval, datetime3, datetime4
                        )

                        self.http_clients_and_strategies[
                            '{}_{}_{}_{} T{} - {}'.format(
                                strategy['name'], exchange.lower(),
                                symbol, interval, datetime1, datetime4
                            )
                        ] = {
                            'http_client1': http_client1,
                            'http_client2': http_client2,
                            'http_client3': http_client3,
                            'strategy': strategy['class']
                        }
            except:
                pass

        if len(self.http_clients_and_strategies) == 0:
            exchange = optimization['exchange']
            symbol = optimization['symbol']
            interval = optimization['interval']
            datetime1 = optimization['date/time #1']
            datetime2 = optimization['date/time #2']
            datetime3 = optimization['date/time #3']
            datetime4 = optimization['date/time #4']

            if exchange == 'binance':
                http_client1 = http_clients[0]()
                http_client2 = http_clients[0]()
                http_client3 = http_clients[0]()
            elif exchange == 'bybit':
                http_client1 = http_clients[1]()
                http_client2 = http_clients[1]()
                http_client3 = http_clients[1]()

            http_client1.get_data(symbol, interval, datetime1, datetime2)
            http_client2.get_data(symbol, interval, datetime2, datetime3)
            http_client3.get_data(symbol, interval, datetime3, datetime4)

            self.http_clients_and_strategies[
                '{}_{}_{}_{} T{} - {}'.format(
                    strategies[optimization['strategy']]['name'],
                    exchange.lower(), symbol, interval, datetime1, datetime4
                )
            ] = {
                'http_client1': http_client1,
                'http_client2': http_client2,
                'http_client3': http_client3,
                'strategy': strategies[optimization['strategy']]['class']
            }

    def create(self):
        samples = [
            [               
                r.choice(j) 
                    for j in self.strategy.opt_parameters.values()
            ]
            for i in range(self.population_size)
        ]
        self.population = {
            k: v for k, v in zip(
                map(
                    partial(self.fit, http_client=self.http_client1), samples
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
        if r.randint(0, 1) == 0:
            score = max(self.population)
            parent_1 = self.population[score]
            population_copy = self.population.copy()
            del population_copy[score]
            parent_2 = r.choice(list(population_copy.values()))
            self.parents = [parent_1, parent_2]
        else:
            parents = r.sample(list(self.population.values()), 2)
            self.parents = [parents[0], parents[1]]

    def recombine(self):
        r_number = r.randint(0, 1)

        if r_number == 0:
            delimiter = r.randint(1, self.sample_length - 1)
            self.child = (self.parents[0][:delimiter] 
                        + self.parents[1][delimiter:])
        else:
            delimiter_1 = r.randint(1, self.sample_length // 2 - 1)
            delimiter_2 = r.randint(
                self.sample_length // 2 + 1, self.sample_length - 1)
            self.child = (self.parents[0][:delimiter_1]
                        + self.parents[1][delimiter_1:delimiter_2]
                        + self.parents[0][delimiter_2:])

    def mutate(self):
        if r.randint(1, 100) <= 95:
            gene_num = r.randint(0, self.sample_length - 1)
            gene_value = r.choice(
                list(self.strategy.opt_parameters.values())[gene_num]
            )
            self.child[gene_num] = gene_value
        else:
            for i in range(len(self.child)):
                self.child[i] = r.choice(
                    list(self.strategy.opt_parameters.values())[i]
                )

    def expand(self):
        self.population[self.fit(self.child, self.http_client1)] = self.child

    def kill(self):
        while len(self.population) > self.max_population_size:
            del self.population[min(self.population)]

    def elect(self):
        best_samples = dict()

        for i in range(self.output_results):
            try:
                best_score = max(self.population)
                best_samples[best_score] = self.population[best_score]
                del self.population[best_score]
            except:
                break

        return best_samples

    def validate(self, mode):
        if mode == 'intermediate':
            http_client = self.http_client2
        elif mode == 'final':
            http_client = self.http_client3

        validation_population = {
            k: v for k, v in zip(
                map(
                    partial(self.fit, http_client=http_client),
                    self.population.values()
                ),
                self.population.items()
            )
        }
        population_size = int(len(self.population) * 0.25)
        self.population.clear()

        for i in range(population_size):
            try:
                best_score = max(validation_population)
                old_score = validation_population[best_score][0]
                sample = validation_population[best_score][1]
                self.population[old_score] = sample
                del validation_population[best_score]
            except:
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
            self.http_client3 = http_client_and_strategy[1]['http_client3']
            self.strategy = http_client_and_strategy[1]['strategy']
            self.create()

            for j in range(1, self.iterations + 1):
                self.select()
                self.recombine()
                self.mutate()
                self.expand()
                self.kill()

                if j % 1000 == 0:
                    self.validate('intermediate')

            self.validate('final')
            best_samples.update(self.elect())
            print(
                'Оптимизация #{} для {} завершена.'.format(
                    i + 1, http_client_and_strategy[0][
                        : http_client_and_strategy[0].find(' ')
                    ]
                )
            )

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