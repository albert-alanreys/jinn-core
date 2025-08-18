import json
import multiprocessing
import os
import random
from logging import getLogger

from src.infrastructure.clients.messaging.telegram import TelegramClient


class OptimizationService:
    """
    Core service responsible for optimizing trading strategy parameters.

    Performs parameter optimization across multiple strategies in parallel,
    using a combination of selection, recombination and mutation operations.
    """

    def __init__(self, settings: dict, strategy_contexts: dict) -> None:
        """
        Initialize OptimizationService with strategy contexts.

        Args:
            settings (dict): Dictionary of optimization settings
            strategy_contexts (dict): Dictionary of strategy contexts
        """

        self.iterations = settings['iterations']
        self.population_size = settings['population_size']
        self.max_population_size = settings['max_population_size']
        self.max_processes = settings['max_processes']

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
                item['market_data']['symbol'],
                str(item['market_data']['interval']),
                f"{item['market_data']['start']} → "
                f"{item['market_data']['end']}"
            ])
            for item in self.strategy_contexts.values()
        ]
        self.logger.info(f"Optimization started for:\n{'\n'.join(summary)}")
        self.telegram_client.send_message('🔥 Optimization started')

        with multiprocessing.Pool(self.max_processes) as pool:
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
            list: Best parameters found during optimization
        """

        self._init_optimization(strategy_context)

        for _ in range(3):
            self._create()

            for _ in range(self.iterations):
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
        population dictionary, best parameters list, and parameter keys.

        Args:
            strategy_context (dict): Context dictionary for the strategy
        """

        self.strategy = strategy_context['type']
        self.client = strategy_context['client']

        self.train_data = self._split_market_data(
            market_data=strategy_context['market_data'],
            train=True
        )
        self.test_data = self._split_market_data(
            market_data=strategy_context['market_data'],
            train=False
        )

        self.population = {}
        self.best_params = []
        
        self.param_keys = list(self.strategy.opt_params.keys())

    def _split_market_data(self, market_data: dict, train: bool = True) -> dict:
        """
        Split market data into train (70%) or test (30%) parts.
        
        Args:
            market_data: Original market data dictionary
            train: If True, returns training part (70%), else test part (30%)
        
        Returns:
            Dictionary with same structure but split arrays
        """
        
        split_idx = int(len(market_data['klines']) * 0.7)
        
        if train:
            slice_range = slice(None, split_idx)
        else:
            slice_range = slice(split_idx, None)
        
        split_data = {
            'symbol': market_data['symbol'],
            'interval': market_data['interval'],
            'start': market_data['start'],
            'end': market_data['end'],
            'p_precision': market_data['p_precision'],
            'q_precision': market_data['q_precision'],
            'klines': market_data['klines'][slice_range],
            'feeds': {'klines': {}}
        }
        
        if market_data.get('feeds'):
            for feed_name, feed_data in market_data['feeds']['klines'].items():
                split_data['feeds']['klines'][feed_name] = feed_data[slice_range]
        
        return split_data


    def _create(self) -> None:
        """
        Create initial population of random parameter combinations.

        Generates population_size random parameter dictionaries
        from strategy's optimization parameter space, evaluates
        their fitness on training data, and stores them
        in population dictionary.
        """

        samples = [
            {
                param_name: random.choice(param_values)
                for param_name, param_values in (
                    self.strategy.opt_params.items()
                )
            }
            for _ in range(self.population_size)
        ]

        for sample in samples:
            fitness = self._evaluate(sample, self.train_data)
            sample_key = self._dict_to_key(sample)
            self.population[fitness] = sample_key

    def _dict_to_key(self, param_dict: dict) -> tuple:
        """
        Convert parameter dictionary to hashable tuple for population storage.

        Args:
            param_dict (dict): Parameter dictionary

        Returns:
            tuple: Hashable representation of parameter values
        """
        return tuple(param_dict[key] for key in self.param_keys)

    def _key_to_dict(self, param_key: tuple) -> dict:
        """
        Convert parameter tuple back to dictionary.

        Args:
            param_key (tuple): Hashable parameter representation

        Returns:
            dict: Parameter dictionary
        """
        return dict(zip(self.param_keys, param_key))

    def _evaluate(self, sample_dict: dict, market_data: dict) -> float:
        """
        Evaluate strategy performance with given parameters.

        Instantiates strategy with provided parameter dictionary,
        runs calculation on market data, and computes fitness score
        based on completed deals performance.

        Args:
            sample_dict (dict): Parameter dictionary to evaluate
            market_data (dict): Dataset to evaluate against

        Returns:
            float: Fitness score (performance metric)
        """

        strategy_instance = self.strategy(self.client, params=sample_dict)
        strategy_instance.calculate(market_data)

        score = strategy_instance.completed_deals_log[:, 8].sum()
        return score

    def _select(self) -> None:
        """
        Select two parent samples for recombination.

        Uses tournament selection: 50% chance to select best individual
        plus random individual, 50% chance to select two random individuals.
        Selected parents are stored in self.parents as dictionaries.
        """

        if random.randint(0, 1) == 0:
            best_score = max(self.population)
            parent_1_key = self.population[best_score]
            parent_1 = self._key_to_dict(parent_1_key)

            population_copy = self.population.copy()
            population_copy.pop(best_score)

            parent_2_key = random.choice(list(population_copy.values()))
            parent_2 = self._key_to_dict(parent_2_key)
            
            self.parents = [parent_1, parent_2]
        else:
            parent_keys = random.sample(list(self.population.values()), 2)
            self.parents = [self._key_to_dict(key) for key in parent_keys]

    def _recombine(self) -> None:
        """
        Create offspring through crossover of selected parents.

        Implements two crossover strategies:
        - Single-point crossover: splits parameter list at random position
        - Two-point crossover: exchanges middle segment between parents
        
        Resulting child is stored in self.child as dictionary.
        """

        param_count = len(self.param_keys)
        r_number = random.randint(0, 1)

        if r_number == 0:
            # Single-point crossover
            delimiter = random.randint(1, param_count - 1)
            
            self.child = {}
            for i, param_name in enumerate(self.param_keys):
                if i < delimiter:
                    self.child[param_name] = self.parents[0][param_name]
                else:
                    self.child[param_name] = self.parents[1][param_name]
        else:
            # Two-point crossover
            delimiter_1 = random.randint(1, param_count // 2 - 1)
            delimiter_2 = random.randint(
                param_count // 2 + 1, param_count - 1
            )

            self.child = {}
            for i, param_name in enumerate(self.param_keys):
                if i < delimiter_1 or i >= delimiter_2:
                    self.child[param_name] = self.parents[0][param_name]
                else:
                    self.child[param_name] = self.parents[1][param_name]

    def _mutate(self) -> None:
        """
        Apply mutation to the offspring.

        With 90% probability mutates single random parameter,
        with 10% probability mutates all parameters.
        Mutation selects random values from corresponding parameter ranges.
        """

        if random.random() <= 0.9:
            # Mutate single parameter
            param_name = random.choice(self.param_keys)
            param_values = self.strategy.opt_params[param_name]
            self.child[param_name] = random.choice(param_values)
        else:
            # Mutate all parameters
            for param_name in self.param_keys:
                param_values = self.strategy.opt_params[param_name]
                self.child[param_name] = random.choice(param_values)

    def _expand(self) -> None:
        """
        Add mutated offspring to population.

        Evaluates fitness of the child on training data and
        adds it to the population dictionary.
        """

        fitness = self._evaluate(self.child, self.train_data)
        child_key = self._dict_to_key(self.child)
        self.population[fitness] = child_key

    def _kill(self) -> None:
        """
        Remove worst individuals to maintain population size.

        Removes individuals with lowest fitness scores until
        population size is within max_population_size limit.
        """

        while len(self.population) > self.max_population_size:
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

    def _get_best_sample(self) -> dict:
        """
        Select best parameter set based on combined train/test performance.

        Evaluates all population samples on test data and selects
        the one with highest combined fitness (50% train + 50% test).

        Returns:
            dict: Best parameter dictionary considering
                  both training and test results
        """

        best_score = float('-inf')
        best_sample = None

        for train_fitness, sample_key in self.population.items():
            sample_dict = self._key_to_dict(sample_key)
            test_fitness = self._evaluate(sample_dict, self.test_data)
            combined_fitness = 0.5 * train_fitness + 0.5 * test_fitness

            if combined_fitness > best_score:
                best_score = combined_fitness
                best_sample = sample_dict

        return best_sample

    def _save_params(self) -> None:
        """
        Save optimized parameters to strategy JSON files.

        Preserves existing optimization results while adding new ones.
        Files are organized by exchange/symbol/interval structure
        and stored in strategy-specific optimization directories.
        """

        for context in self.strategy_contexts.values():
            filename = (
                f'{context['client'].EXCHANGE}_'
                f'{context['market_data']['symbol']}_'
                f'{context['market_data']['interval']}.json'
            )
            file_path = os.path.abspath(
                os.path.join(
                    'src',
                    'strategies',
                    context['name'].lower(),
                    'optimization',
                    filename
                )
            )

            new_items = [
                {
                    'period': {
                        'start': context['market_data']['start'],
                        'end': context['market_data']['end']
                    },
                    'params': params
                }
                for params in context['best_params']
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