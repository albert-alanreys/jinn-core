import json
import multiprocessing
import os
import random
from logging import getLogger

from src.infrastructure.clients.messaging.telegram import TelegramClient


class OptimizationService:
    """
    Core service responsible for optimizing
    trading strategy parameters.

    Performs parameter optimization across multiple strategies in parallel,
    using a combination of selection, recombination and mutation operations.

    Args:
        strategy_contexts (dict): Dictionary of strategy contexts from Builder
    """

    ITERATIONS = 1000
    POPULATION_SIZE = 100
    MAX_POPULATION_SIZE = 500

    def __init__(self, strategy_contexts: dict) -> None:
        self.strategy_contexts = strategy_contexts

        self.telegram_client = TelegramClient()
        self.logger = getLogger(__name__)

    def run(self) -> None:
        """
        Execute the optimization process.

        Manages the complete optimization workflow:
        1. Logs optimization start.
        2. Runs parallel optimizations.
        3. Saves best parameters.
        4. Logs completion.
        """

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
        self.telegram_client.send_message('🔥 Optimization started')

        with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
            best_params = pool.map(
                func=self._optimize,
                iterable=self.strategy_contexts.values()
            )

        for cid, params in zip(self.strategy_contexts, best_params):
            self.strategy_contexts[cid]['best_params'] = params

        self._save_params()

        self.logger.info('Optimization completed')
        self.telegram_client.send_message('✅ Optimization completed')

    def _optimize(self, strategy_context: dict) -> list:
        """
        Optimize parameters for a single strategy.

        Executes genetic algorithm optimization cycle consisting of:
        population creation, selection, recombination, mutation, and 
        population management over multiple iterations.

        Args:
            strategy_context (dict): Context dictionary for the strategy
                                     containing type, client, and market data

        Returns:
            list: Best parameters found during optimization (3 parameter sets)
        """

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
        """
        Initialize optimization variables for a single strategy.

        Sets up strategy instance, client, training/test data,
        population dictionary, and best parameters list.

        Args:
            strategy_context (dict): Context dictionary for the strategy
        """

        self.strategy = strategy_context['type']
        self.client = strategy_context['client']
        self.train_data = strategy_context['market_data']['train']
        self.test_data = strategy_context['market_data']['test']

        self.population = {}
        self.best_params = []

    def _create(self) -> None:
        """
        Create initial population of random parameter combinations.

        Generates POPULATION_SIZE random samples from strategy's optimization
        parameter space, evaluates their fitness on training data, and
        stores them in population dictionary.
        """

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
        """
        Evaluate strategy performance with given parameters.

        Instantiates strategy with provided parameters, runs calculation
        on market data, and computes fitness score based on completed
        deals performance relative to initial capital.

        Args:
            sample (list): Parameter set to evaluate
            market_data (dict): Dataset to evaluate against

        Returns:
            float: Fitness score (performance metric as percentage)
        """

        strategy_instance = self.strategy(self.client, opt_params=sample)
        strategy_instance.calculate(market_data)

        score = strategy_instance.completed_deals_log[:, 8].sum()
        return score

    def _select(self) -> None:
        """
        Select two parent samples for recombination.

        Uses tournament selection: 50% chance to select best individual
        plus random individual, 50% chance to select two random individuals.
        Selected parents are stored in self.parents.
        """

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
        """
        Create offspring through crossover of selected parents.

        Implements two crossover strategies:
        - Single-point crossover: splits at random position
        - Two-point crossover: exchanges middle segment between parents
        
        Resulting child is stored in self.child.
        """

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
        """
        Apply mutation to the offspring.

        With 90% probability mutates single random gene,
        with 10% probability mutates all genes.
        Mutation selects random values from corresponding parameter ranges.
        """

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
        """
        Add mutated offspring to population.

        Evaluates fitness of the child on training data and
        adds it to the population dictionary.
        """

        fitness = self._evaluate(self.child, self.train_data)
        self.population[fitness] = self.child

    def _kill(self) -> None:
        """
        Remove worst individuals to maintain population size.

        Removes individuals with lowest fitness scores until
        population size is within MAX_POPULATION_SIZE limit.
        """

        while len(self.population) > self.MAX_POPULATION_SIZE:
            self.population.pop(min(self.population))

    def _destroy(self) -> None:
        """
        Catastrophic population reduction event.

        With 0.1% probability removes bottom 50% of population
        to prevent premature convergence and maintain diversity.
        """

        if random.random() > 0.001:
            return

        sorted_population = sorted(
            self.population.items(),
            key=lambda x: x[0]
        )

        for i in range(int(len(self.population) * 0.5)):
            self.population.pop(sorted_population[i][0])

    def _get_best_sample(self) -> list:
        """
        Select best parameter set based on combined train/test performance.

        Evaluates all population samples on test data and selects
        the one with highest combined fitness (50% train + 50% test).

        Returns:
            list: Best parameter sample considering
                  both training and test results
        """

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
        """
        Save optimized parameters to strategy JSON files.

        Preserves existing optimization results while adding new ones.
        Files are organized by exchange/market/symbol/interval structure
        and stored in strategy-specific optimization directories.
        """

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