import json
import multiprocessing
import os
import random
from logging import getLogger

from src.services.automation.api_clients.telegram import TelegramClient


class Optimizer:
    ITERATIONS = 200
    POPULATION_SIZE = 100
    MAX_POPULATION_SIZE = 500

    def __init__(self, strategy_contexts: dict) -> None:
        self.strategy_contexts = strategy_contexts

        self.telegram_client = TelegramClient()
        self.logger = getLogger(__name__)

    def run(self) -> None:
        summary = [
            ' | '.join([
                item['name'],
                item['client'].EXCHANGE,
                item['market_data']['train']['market'].value,
                item['market_data']['train']['symbol'],
                str(item['market_data']['train']['interval']),
                f"{item['market_data']['train']['start']} → "
                f"{item['market_data']['test']['end']}"
            ])
            for item in self.strategy_contexts.values()
        ]
        self.logger.info(f"Optimization started for:\n{'\n'.join(summary)}")
        self.telegram_client.send_message('🔥 Оптимизация началась')

        with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
            best_params = pool.map(
                func=self._optimize,
                iterable=self.strategy_contexts.values()
            )

        for cid, params in zip(self.strategy_contexts, best_params):
            self.strategy_contexts[cid]['best_params'] = params

        self._save_params()

        self.logger.info('Optimization completed')
        self.telegram_client.send_message('✅ Оптимизация завершена')

    def _optimize(self, strategy_context: dict) -> list:
        self._init_optimization(strategy_context)

        for _ in range(3):
            self._create()

            for _ in range(self.ITERATIONS):
                self._select()
                self._recombine()
                self._mutate()
                self._expand()
                self._kill()
                self._destroy()

            self.best_params.append(self._get_best_sample())
            self.population.clear()

        return self.best_params

    def _init_optimization(self, strategy_context: dict) -> None:
        self.strategy = strategy_context['type']
        self.client = strategy_context['client']
        self.train_data = strategy_context['market_data']['train']
        self.test_data = strategy_context['market_data']['test']

        self.population = {}
        self.best_params = []

    def _create(self) -> None:
        samples = [
            [               
                random.choice(values)
                for values in self.strategy.opt_params.values()
            ]
            for _ in range(self.POPULATION_SIZE)
        ]

        for sample in samples:
            fitness = self._evaluate(sample, self.train_data)
            self.population[fitness] = sample

        self.sample_len = len(self.strategy.opt_params)

    def _evaluate(self, sample: list, market_data: dict) -> float:
        strategy_instance = self.strategy(self.client, opt_params=sample)
        strategy_instance.start(market_data)

        score = round(
            strategy_instance.completed_deals_log[8::13].sum() /
            strategy_instance.params['initial_capital'] * 100,
            2
        )
        return score

    def _select(self) -> None:
        if random.randint(0, 1) == 0:
            best_score = max(self.population)
            parent_1 = self.population[best_score]

            population_copy = self.population.copy()
            population_copy.pop(best_score)

            parent_2 = random.choice(list(population_copy.values()))
            self.parents = [parent_1, parent_2]
        else:
            self.parents = random.sample(list(self.population.values()), 2)

    def _recombine(self) -> None:
        r_number = random.randint(0, 1)

        if r_number == 0:
            delimiter = random.randint(1, self.sample_len - 1)
            self.child = (
                self.parents[0][:delimiter] + self.parents[1][delimiter:]
            )
        else:
            delimiter_1 = random.randint(1, self.sample_len // 2 - 1)
            delimiter_2 = random.randint(
                self.sample_len // 2 + 1, self.sample_len - 1
            )

            self.child = (
                self.parents[0][:delimiter_1] +
                self.parents[1][delimiter_1:delimiter_2] +
                self.parents[0][delimiter_2:]
            )

    def _mutate(self) -> None:
        if random.random() <= 0.9:
            gene_num = random.randint(0, self.sample_len - 1)
            gene_value = random.choice(
                list(self.strategy.opt_params.values())[gene_num]
            )
            self.child[gene_num] = gene_value
        else:
            for i in range(len(self.child)):
                self.child[i] = random.choice(
                    list(self.strategy.opt_params.values())[i]
                )

    def _expand(self) -> None:
        fitness = self._evaluate(self.child, self.train_data)
        self.population[fitness] = self.child

    def _kill(self) -> None:
        while len(self.population) > self.MAX_POPULATION_SIZE:
            self.population.pop(min(self.population))

    def _destroy(self) -> None:
        if random.random() > 0.001:
            return

        sorted_population = sorted(
            self.population.items(),
            key=lambda x: x[0]
        )

        for i in range(int(len(self.population) * 0.5)):
            self.population.pop(sorted_population[i][0])

    def _get_best_sample(self) -> None:
        best_score = float('-inf')
        best_sample = None

        for train_fitness, sample in self.population.items():
            test_fitness = self._evaluate(sample, self.test_data)
            combined_fitness = 0.5 * train_fitness + 0.5 * test_fitness

            if combined_fitness > best_score:
                best_score = combined_fitness
                best_sample = sample

        return best_sample

    def _save_params(self) -> None:
        for strategy in self.strategy_contexts.values():
            filename = (
                f'{strategy['client'].EXCHANGE}_'
                f'{strategy['market_data']['train']['market'].value}_'
                f'{strategy['market_data']['train']['symbol']}_'
                f'{strategy['market_data']['train']['interval']}.json'
            )
            file_path = os.path.abspath(
                os.path.join(
                    'src',
                    'strategies',
                    strategy['name'].lower(),
                    'optimization',
                    filename
                )
            )

            new_items = [
                {
                    'period': {
                        'start': strategy['market_data']['train']['start'],
                        'end': strategy['market_data']['test']['end']
                    },
                    'params': dict(
                        zip(strategy['type'].opt_params.keys(), params)
                    )
                }
                for params in strategy['best_params']
            ]
            existing_items = []

            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    try:
                        existing_items = json.load(file)
                    except json.JSONDecodeError:
                        pass

            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(existing_items + new_items, file, indent=4)