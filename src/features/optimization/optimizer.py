from __future__ import annotations
from os import getenv
from random import choice, randint, sample
from typing import Any, TYPE_CHECKING

from .config import OptimizationConfig
from .utils import (
    create_train_test_windows,
    create_window_data,
    latin_hypercube_sampling
)

if TYPE_CHECKING:
    from multiprocessing import Queue
    from src.core.providers import MarketData
    from .models import StrategyContext


class StrategyOptimizer:
    """
    Genetic algorithm optimizer for trading strategy optimization.
    
    Implements a genetic algorithm with selection, recombination, mutation,
    and population management to find optimal parameter sets for strategies.
    """

    def __init__(self) -> None:
        """
        Initialize the strategy optimizer with configuration
        from environment variables.
        
        Loads optimization parameters from environment variables
        with fallback to default values from OptimizationConfig.
        
        Supported environment variables:
        - OPTIMIZATION_ITERATIONS: Number of genetic algorithm iterations
        - OPTIMIZATION_RUNS: Number of independent optimization runs
        - POPULATION_SIZE: Initial population size
        - MAX_POPULATION_SIZE: Maximum allowed population size
        - TRAIN_WINDOW: Training data window size
        - TEST_WINDOW: Test data window size
        """

        self.config = OptimizationConfig()
        
        env_mapping = {
            'OPTIMIZATION_ITERATIONS': ('iterations', int),
            'OPTIMIZATION_RUNS': ('optimization_runs', int),
            'POPULATION_SIZE': ('population_size', int),
            'MAX_POPULATION_SIZE': ('max_population_size', int),
            'TRAIN_WINDOW': ('train_window', float),
            'TEST_WINDOW': ('test_window', float),
        }
        
        for env_var, (attr_name, converter) in env_mapping.items():
            if value := getenv(env_var):
                setattr(self.config, attr_name, converter(value))

    def optimize(self, context: StrategyContext) -> list[dict[str, Any]]:
        """
        Optimize parameters for a single strategy using genetic algorithm.

        Executes genetic algorithm optimization cycle consisting of:
        population creation, selection, recombination, mutation, and 
        population management over multiple iterations and runs.

        Args:
            context: Strategy context package

        Returns:
            list: Best parameters found during optimization
        """

        self._init_optimization(context)

        for _ in range(self.config.optimization_runs):
            self._create_population()

            for _ in range(self.config.iterations):
                self._select()
                self._recombine()
                self._mutate()
                self._expand()
                self._kill()
                self._destroy()

            self.best_params.append(self._get_best_sample())
            self.population.clear()

        return self.best_params

    def _init_optimization(self, context: StrategyContext) -> None:
        """
        Initialize optimization variables for a single strategy.

        Sets up strategy instance, client, training/test data,
        population dictionary, best parameters list, and parameter keys.

        Args:
            context: Strategy context package
        """

        self.strategy_class = context['strategy_class']

        windows = create_train_test_windows(
            market_data=context['market_data'],
            config=self.config
        )

        self.train_data = create_window_data(
            market_data=context['market_data'],
            window=windows,
            data_type='train'
        )
        self.test_data = create_window_data(
            market_data=context['market_data'],
            window=windows,
            data_type='test'
        )

        self.population = {}
        self.best_params = []
        
        self.param_keys = list(self.strategy_class.opt_params.keys())

    def _create_population(self) -> None:
        """
        Create initial population of candidate parameter sets.

        Combines random sampling, Latin Hypercube Sampling, and
        extreme values to improve diversity and convergence speed.
        """

        population = []
        opt_params = self.strategy_class.opt_params

        # Random sampling (30%)
        random_count = int(self.config.population_size * 0.3)
        for _ in range(random_count):
            population.append({
                param_name: choice(param_values)
                for param_name, param_values in opt_params.items()
            })

        # Latin Hypercube Sampling (40%)
        lhs_count = int(self.config.population_size * 0.4)
        population.extend(
            latin_hypercube_sampling(opt_params, lhs_count)
        )

        # Extreme values (20%)
        extreme_count = int(self.config.population_size * 0.2)
        for _ in range(extreme_count):
            individual = {
                param_name: choice([param_values[0], param_values[-1]])
                for param_name, param_values in opt_params.items()
            }
            population.append(individual)

        # Fill remaining with random samples if needed
        while len(population) < self.config.population_size:
            population.append({
                param_name: choice(param_values)
                for param_name, param_values in opt_params.items()
            })

        # Evaluate and add to population
        for individual in population:
            fitness = self._evaluate(individual, self.train_data)
            sample_key = self._dict_to_key(individual)
            self.population[fitness] = sample_key

    def _dict_to_key(self, param_dict: dict[str, Any]) -> tuple[Any, ...]:
        """
        Convert parameter dictionary to hashable tuple for population storage.

        Args:
            param_dict: Parameter dictionary with parameter names as keys

        Returns:
            tuple: Hashable representation of parameter values
        """
        return tuple(param_dict[key] for key in self.param_keys)

    def _key_to_dict(self, param_key: tuple[Any, ...]) -> dict[str, Any]:
        """
        Convert parameter tuple back to dictionary.

        Args:
            param_key: Hashable parameter representation as tuple

        Returns:
            dict: Parameter dictionary
        """
        return dict(zip(self.param_keys, param_key))

    def _evaluate(
        self,
        sample_dict: dict[str, Any],
        market_data: MarketData
    ) -> float:
        """
        Evaluate strategy performance with given parameters.

        Instantiates strategy with provided parameter dictionary,
        runs calculation on market data, and computes fitness score
        based on completed deals performance.

        Args:
            sample_dict: Parameter dictionary to evaluate
            market_data: Market data package

        Returns:
            float: Fitness score (performance metric)
        """

        strategy = self.strategy_class(sample_dict)
        strategy.calculate(market_data)

        score = strategy.completed_deals_log[:, 8].sum()
        return score

    def _select(self) -> None:
        """
        Select two parent samples for recombination.

        Uses tournament selection: 50% chance to select best individual
        plus random individual, 50% chance to select two random individuals.
        Selected parents are stored in self.parents as dictionaries.
        """

        if randint(0, 1) == 0:
            best_score = max(self.population)
            parent_1_key = self.population[best_score]
            parent_1 = self._key_to_dict(parent_1_key)

            population_copy = self.population.copy()
            population_copy.pop(best_score)

            parent_2_key = choice(list(population_copy.values()))
            parent_2 = self._key_to_dict(parent_2_key)
            
            self.parents = [parent_1, parent_2]
        else:
            parent_keys = sample(list(self.population.values()), 2)
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
        r_number = randint(0, 1)

        if r_number == 0:
            # Single-point crossover
            delimiter = randint(1, param_count - 1)
            
            self.child = {}
            for i, param_name in enumerate(self.param_keys):
                if i < delimiter:
                    self.child[param_name] = self.parents[0][param_name]
                else:
                    self.child[param_name] = self.parents[1][param_name]
        else:
            # Two-point crossover
            delimiter_1 = randint(1, param_count // 2 - 1)
            delimiter_2 = randint(
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

        if randint(1, 10) <= 9:
            # Mutate single parameter
            param_name = choice(self.param_keys)
            param_values = self.strategy_class.opt_params[param_name]
            self.child[param_name] = choice(param_values)
        else:
            # Mutate all parameters
            for param_name in self.param_keys:
                param_values = self.strategy_class.opt_params[param_name]
                self.child[param_name] = choice(param_values)

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

        while len(self.population) > self.config.max_population_size:
            self.population.pop(min(self.population))

    def _destroy(self) -> None:
        """
        Catastrophic population reduction event.

        With 0.1% probability removes bottom 50% of population
        to prevent premature convergence and maintain diversity.
        """

        if randint(1, 1000) != 1:
            return

        sorted_population = sorted(
            self.population.items(),
            key=lambda x: x[0]
        )

        for i in range(int(len(self.population) * 0.5)):
            self.population.pop(sorted_population[i][0])

    def _get_best_sample(self) -> dict[str, Any]:
        """
        Select best parameter set based on combined train/test performance.

        Evaluates all population samples on test data and selects
        the one with highest combined fitness (50% train + 50% test).

        Returns:
            dict[str, Any]: Best parameter dictionary considering
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


def optimize_worker(
    context_id: str,
    context: StrategyContext,
    results_queue: Queue[tuple[str, list[dict[str, Any]] | None, str | None]]
) -> None:
    """
    Optimize trading strategy in separate worker process.

    Runs strategy optimization for given context and puts results
    into queue for main process. Handles exceptions and returns
    error information if optimization fails.

    Args:
        context_id: Unique context identifier
        context: Strategy optimization context
        results_queue: Multiprocessing queue
    """
    
    try:
        optimizer = StrategyOptimizer()
        params = optimizer.optimize(context)
        results_queue.put((context_id, params, None))
    except Exception as e:
        results_queue.put((context_id, None, f'{type(e).__name__}: {e}'))