import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from numpy import ndarray


class GA:
    ITERATIONS = 5000
    POPULATION_SIZE = 100
    MAX_POPULATION_SIZE = 500

    def __init__(self, strategy_state: dict) -> None:
        self.strategy = strategy_state['type']
        self.client = strategy_state['client']
        self.market_data = strategy_state['market_data']
        self.train_data = strategy_state['train_data']
        self.test_data = strategy_state['test_data']

        self.population = {}
        self.best_samples = []

    def fit(self) -> None:
        for _ in range(3):
            self._create()

            for _ in range(self.ITERATIONS):
                self._select()
                self._recombine()
                self._mutate()
                self._expand()
                self._kill()
                self._destroy()

            self._elect()
            self.population.clear()

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

    def _evaluate(self, sample: list, fold: 'ndarray') -> float:
        market_data = self.market_data.copy()
        market_data['klines'] = fold

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

    def _elect(self) -> None:
        best_score = float('-inf')
        best_sample = None

        for train_fitness, sample in self.population.items():
            test_fitness = self._evaluate(sample, self.test_data)
            combined_fitness = 0.5 * train_fitness + 0.5 * test_fitness

            if combined_fitness > best_score:
                best_score = combined_fitness
                best_sample = sample

        self.best_samples.append(best_sample)