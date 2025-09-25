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
        Initialize optimization variables for a strategy context.

        Sets up strategy class, training/test data windows,
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
        Create initial population of candidate parameter sets
        using multiple sampling methods.

        Uses a diversified approach:
        - Random sampling (30%): Random selection from parameter ranges
        - Latin Hypercube Sampling (40%): Space-filling statistical sampling 
        - Extreme values (20%): Combinations of min/max parameter values
        - Random fill (remaining): Additional random samples if needed
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
        unique_samples = len(set(self.population.values()))
        diversity_ratio = unique_samples / population_size
        
        # Adaptive tournament size (2-4 based on diversity)
        if diversity_ratio > 0.7:
            tournament_size = 2
        elif diversity_ratio > 0.4:
            tournament_size = 3
        else:
            tournament_size = 4
        
        self.parents = []
        
        for _ in range(2):
            fitness_scores = list(self.population.keys())
            tournament_scores = sample(
                fitness_scores, min(tournament_size, population_size)
            )
            
            # Winner selection with elite bias
            if randint(1, 100) <= 80:
                winner_score = max(tournament_scores)
            else:
                winner_score = choice(tournament_scores)
            
            winner_key = self.population[winner_score]
            parent = self._key_to_dict(winner_key)
            self.parents.append(parent)
            
            if len(fitness_scores) > 1:
                fitness_scores.remove(winner_score)

    def _recombine(self) -> None:
        """
        Create offspring through balanced crossover of selected parents.

        Implements three crossover strategies:
        - Uniform crossover (50%): Parameter-wise random inheritance
        - Single-point crossover (30%): Classic split-point crossover
        - Arithmetic crossover (20%): Blend for numerical parameters
        """
        
        param_count = len(self.param_keys)
        crossover_type = randint(1, 100)
        
        self.child = {}
        
        if crossover_type <= 50:
            # Uniform crossover - each parameter from random parent
            for param_name in self.param_keys:
                parent_idx = randint(0, 1)
                self.child[param_name] = self.parents[parent_idx][param_name]
                
        elif crossover_type <= 80:
            # Single-point crossover
            delimiter = randint(1, param_count - 1)
            
            for i, param_name in enumerate(self.param_keys):
                if i < delimiter:
                    self.child[param_name] = self.parents[0][param_name]
                else:
                    self.child[param_name] = self.parents[1][param_name]
        else:
            # Arithmetic crossover for numerical, random for boolean
            for param_name in self.param_keys:
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
        Apply adaptive mutation to the offspring.

        Implements balanced mutation strategies:
        - Adaptive mutation rate based on population diversity
        - Multi-parameter mutation with decreasing probability
        - Gaussian-style mutation for numerical parameters
        - Boundary exploration for all parameter types
        """
        
        # Calculate adaptive mutation rate based on population diversity
        population_diversity = len(set(self.population.values())) / len(
            self.population
        )
        base_rate = 0.15
        adaptive_rate = base_rate * (2.0 - population_diversity)
        
        if randint(1, 100) > int(adaptive_rate * 100):
            return
        
        # Select parameters to mutate with decreasing probability
        params_to_mutate = []
        for i, param_name in enumerate(self.param_keys):
            mutation_prob = 70 / (2 ** i) if i < 3 else 10
            if randint(1, 100) <= mutation_prob:
                params_to_mutate.append(param_name)
        
        # Ensure at least one parameter is mutated
        if not params_to_mutate:
            params_to_mutate = [choice(self.param_keys)]
        
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
        Catastrophic population reduction with adaptive triggers.

        Implements diversification strategy to prevent premature convergence:
        - Base 1% chance for catastrophic event
        - Higher probability when population diversity is low
        - Removes bottom 40-60% based on population fitness variance
        - Preserves elite individuals to maintain optimization progress
        """
        
        # Calculate population diversity and fitness variance
        unique_samples = len(set(self.population.values()))
        diversity_ratio = unique_samples / len(self.population)
        
        fitness_values = list(self.population.keys())
        fitness_variance = (
            (max(fitness_values) - min(fitness_values)) / 
            (abs(max(fitness_values)) + 1e-10)
        )
        
        # Adaptive trigger probability
        base_probability = 1
        diversity_factor = max(1, int(5 * (1 - diversity_ratio)))
        variance_factor = max(1, int(3 * (1 - fitness_variance)))
        
        trigger_probability = min(
            15, base_probability * diversity_factor * variance_factor
        )
        
        if randint(1, 100) > trigger_probability:
            return
        
        # Determine destruction intensity based on population state
        if diversity_ratio < 0.3:
            destruction_ratio = randint(50, 70) / 100.0
        elif fitness_variance < 0.1:
            destruction_ratio = randint(40, 55) / 100.0
        else:
            destruction_ratio = randint(35, 45) / 100.0
        
        sorted_population = sorted(
            self.population.items(), key=lambda x: x[0]
        )
        
        individuals_to_remove = int(len(self.population) * destruction_ratio)
        
        for i in range(individuals_to_remove):
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