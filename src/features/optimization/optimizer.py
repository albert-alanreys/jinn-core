from __future__ import annotations
from os import getenv
from random import choice, randint, sample
from typing import TYPE_CHECKING

from .config import OptimizationConfig
from .utils import (
    create_train_test_windows,
    create_window_data,
    latin_hypercube_sampling
)

if TYPE_CHECKING:
    from multiprocessing import Queue
    from src.core.providers import MarketData
    from src.core.strategies.core.models import ParamDict
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

    def optimize(self, context: StrategyContext) -> list[ParamDict]:
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

            self.best_params.append(self._get_best_sample())
            self.population.clear()

        return self.best_params

    def _init_optimization(self, context: StrategyContext) -> None:
        """
        Initialize optimization variables for a strategy context.

        Sets up strategy class, training/test data windows,
        and population dictionary.

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

        self.population: dict[float, ParamDict] = {}
        self.best_params: list[ParamDict] = []

    def _create_population(self) -> None:
        """
        Create initial population of candidate parameter sets
        using multiple sampling methods.

        Uses a diversified approach:
        - Latin Hypercube Sampling (50%): Space-filling statistical sampling
        - Random sampling (30%): Random selection from parameter ranges
        - Extreme values (20%): Boundary parameter values
        """

        population: list[ParamDict] = []
        opt_params = self.strategy_class.opt_params

        # Latin Hypercube Sampling (50%)
        lhs_count = int(self.config.population_size * 0.5)
        individuals = latin_hypercube_sampling(opt_params, lhs_count)
        population.extend(individuals)

        # Random sampling (30%)
        random_count = int(self.config.population_size * 0.3)
        for _ in range(random_count):
            individual = {
                param_name: choice(param_values)
                for param_name, param_values in opt_params.items()
            }
            population.append(individual)

        # Extreme values (20%)
        extreme_count = int(self.config.population_size * 0.2)
        for _ in range(extreme_count):
            individual = {
                param_name: choice([param_values[0], param_values[-1]])
                for param_name, param_values in opt_params.items()
            }
            population.append(individual)

        # Evaluate and add to population
        for individual in population:
            fitness = self._evaluate(individual, self.train_data)
            self.population[fitness] = individual

    def _evaluate(
        self,
        sample_dict: ParamDict,
        market_data: MarketData
    ) -> float:
        """
        Evaluate strategy performance with given parameters.

        Args:
            sample_dict: Dictionary of strategy parameters to test
            market_data: Market data package

        Returns:
            float: Fitness score based on sum of completed deals profit/loss
        """

        strategy = self.strategy_class(sample_dict)
        strategy.__calculate__(market_data)

        score = strategy.completed_deals_log[:, 8].sum()
        return score

    def _select(self) -> None:
        """
        Select two parent samples using adaptive tournament selection.

        Implements efficient tournament selection with adaptive pressure:
        - Tournament size adapts to population diversity
        - Elite bias decreases over iterations to maintain exploration
        """
        
        # Calculate adaptive tournament parameters
        population_size = len(self.population)
        unique_samples = len(set(
            tuple(params.items()) for params in self.population.values()
        ))
        diversity_ratio = unique_samples / population_size
        
        # Adaptive tournament size (2-4 based on diversity)
        if diversity_ratio > 0.7:
            tournament_size = 2
        elif diversity_ratio > 0.4:
            tournament_size = 3
        else:
            tournament_size = 4
        
        self.parents: list[ParamDict] = []
        available_individuals = list(self.population.items())
        
        for _ in range(2):
            if len(available_individuals) < tournament_size:
                tournament_pool = available_individuals.copy()
            else:
                tournament_pool = sample(
                    available_individuals, tournament_size
                )
            
            if randint(1, 100) <= 80:
                winner_fitness, winner_params = max(
                    tournament_pool, key=lambda x: x[0]
                )
            else:
                winner_fitness, winner_params = choice(tournament_pool)
            
            self.parents.append(winner_params)
            
            available_individuals.remove((winner_fitness, winner_params))

    def _recombine(self) -> None:
        """
        Create offspring through balanced crossover of selected parents.

        Implements three crossover strategies:
        - Uniform crossover (50%): Parameter-wise random inheritance
        - Single-point crossover (30%): Classic split-point crossover
        - Arithmetic crossover (20%): Blend for numerical parameters
        """
        
        param_keys = list(self.strategy_class.opt_params.keys())
        param_count = len(param_keys)
        crossover_type = randint(1, 100)
        
        self.child: ParamDict = {}
        
        if crossover_type <= 50:
            # Uniform crossover - each parameter from random parent
            for param_name in param_keys:
                parent_idx = randint(0, 1)
                self.child[param_name] = self.parents[parent_idx][param_name]
                
        elif crossover_type <= 80:
            # Single-point crossover
            delimiter = randint(1, param_count - 1)
            
            for i, param_name in enumerate(param_keys):
                if i < delimiter:
                    self.child[param_name] = self.parents[0][param_name]
                else:
                    self.child[param_name] = self.parents[1][param_name]
        else:
            # Arithmetic crossover for numerical, random for boolean
            for param_name in param_keys:
                parent_1_val = self.parents[0][param_name]
                parent_2_val = self.parents[1][param_name]
                
                if isinstance(parent_1_val, bool):
                    self.child[param_name] = choice(
                        [parent_1_val, parent_2_val]
                    )
                else:
                    param_values = self.strategy_class.opt_params[param_name]
                    alpha = randint(30, 70) / 100.0
                    blended = (
                        alpha * parent_1_val + (1 - alpha) * parent_2_val
                    )
                    
                    # Find closest valid parameter value
                    closest_value = min(
                        param_values, key=lambda x: abs(x - blended)
                    )
                    self.child[param_name] = closest_value

    def _mutate(self) -> None:
        """
        Apply mutation to the offspring.

        Implements mutation strategies:
        - Overall mutation applied probabilistically based on population diversity
        - Each selected parameter mutates with 20% chance
        - Ensures at least one parameter is mutated
        - Gaussian-style mutation for numerical parameters
        - Boundary exploration for all parameter types
        - Simple discrete mutation for small sets of values
        """
        
        # Calculate adaptive mutation rate based on population diversity
        unique_samples = len(set(
            tuple(params.items()) for params in self.population.values()
        ))
        population_diversity = unique_samples / len(self.population)
        
        base_rate = 0.5
        adaptive_rate = base_rate * (2.0 - population_diversity)
        
        if randint(1, 100) > int(adaptive_rate * 100):
            return
        
        param_keys = list(self.strategy_class.opt_params.keys())
        
        # Select parameters to mutate with decreasing probability
        params_to_mutate = [
            param_name for param_name in param_keys if randint(1, 100) <= 20
        ]
        
        # Ensure at least one parameter is mutated
        if not params_to_mutate:
            params_to_mutate = [choice(param_keys)]
        
        for param_name in params_to_mutate:
            param_values = self.strategy_class.opt_params[param_name]
            current_value = self.child[param_name]
            
            if isinstance(current_value, bool):
                self.child[param_name] = not current_value
                
            elif len(param_values) <= 3:
                available_values = [
                    val for val in param_values if val != current_value
                ]
                if available_values:
                    self.child[param_name] = choice(available_values)
            else:
                mutation_type = randint(1, 100)
                
                if mutation_type <= 25:
                    # Boundary mutation
                    self.child[param_name] = choice([
                        param_values[0], param_values[-1]
                    ])
                elif mutation_type <= 60:
                    # Gaussian-style neighbor mutation
                    current_idx = param_values.index(current_value)
                    max_offset = max(1, len(param_values) // 8)
                    offset = randint(-max_offset, max_offset)
                    new_idx = max(0, min(
                        len(param_values) - 1, current_idx + offset
                    ))
                    self.child[param_name] = param_values[new_idx]
                else:
                    # Random mutation
                    self.child[param_name] = choice(param_values)

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
        
        With 1% probability performs catastrophic reduction (40-60%)
        to prevent premature convergence.
        """

        # Catastrophic reduction (0.5% probability)
        if randint(1, 1000) <= 5:
            destruction_ratio = randint(40, 60) / 100.0
            target_size = int(len(self.population) * (1 - destruction_ratio))
        else:
            # Standard population size control
            target_size = self.config.max_population_size
        
        # Remove worst individuals
        while len(self.population) > target_size:
            self.population.pop(min(self.population))

    def _get_best_sample(self) -> ParamDict:
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

        for train_fitness, sample_params in self.population.items():
            test_fitness = self._evaluate(sample_params, self.test_data)
            combined_fitness = 0.5 * train_fitness + 0.5 * test_fitness

            if combined_fitness > best_score:
                best_score = combined_fitness
                best_sample = sample_params

        return best_sample


def optimize_worker(
    context_id: str,
    context: StrategyContext,
    results_queue: Queue[tuple[str, list[ParamDict] | None, str | None]]
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