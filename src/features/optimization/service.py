import json
import os
import random
from concurrent.futures import ProcessPoolExecutor, as_completed
from logging import getLogger
from typing import Any

import numpy as np

from src.infrastructure.messaging import TelegramClient
from .dataclasses import OptimizationConfig
from .utils import (
    latin_hypercube_sampling,
    create_walkforward_windows,
    create_window_data,
)


class OptimizationService:
    """
    Optimization service with modern practices:
    - Walk-Forward Analysis with candle-based windows
    - Adaptive Genetic Algorithm with elitism and adaptive operators
    - Early stopping with convergence detection
    - Smart population initialization (LHS + random + extremes)
    - Parallel fitness evaluation with proper error handling
    - Multi-objective optimization with stability scoring
    - Advanced crossover and mutation strategies
    """

    def __init__(self, strategy_contexts: dict[str, dict[str, Any]]) -> None:
        """
        Initialize the optimization service.

        Args:
            settings: Dictionary of optimization settings
            strategy_contexts: Dictionary of strategy contexts
        """

        self.strategy_contexts = strategy_contexts
        self.config = OptimizationConfig()

        self.telegram_client = TelegramClient()
        self.logger = getLogger(__name__)

    def run(self) -> None:
        """Run optimization for all provided strategy contexts."""

        summary = [
            ' | '.join([
                item['name'],
                item['client'].exchange_name,
                item['market_data']['symbol'],
                str(item['market_data']['interval']),
                f"{item['market_data']['start']} → "
                f"{item['market_data']['end']}"
            ])
            for item in self.strategy_contexts.values()
        ]
        self.logger.info(f"Optimization started for:\n{'\n'.join(summary)}")
        self.telegram_client.send_message('🔥 Optimization started')

        with ProcessPoolExecutor(self.config.max_processes) as executor:
            futures = {
                executor.submit(self._optimize, context): cid
                for cid, context in self.strategy_contexts.items()
            }

            for future in as_completed(futures):
                cid = futures[future]

                try:
                    best_params = future.result()
                    self.strategy_contexts[cid]['best_params'] = best_params
                except Exception as exc:
                    self.logger.error(
                        f'Strategy {cid} optimization failed: {exc}'
                    )
                    self.strategy_contexts[cid]['best_params'] = []

        self._save_params()

        self.logger.info('Optimization completed')
        self.telegram_client.send_message('✅ Optimization completed')

    def _optimize(
        self,
        strategy_context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Run Walk-Forward Analysis optimization for a single strategy context.

        Initializes optimization, builds training/validation windows,
        executes multiple optimization runs, and collects best parameter sets.

        Args:
            strategy_context: Strategy context dictionary

        Returns:
            list[dict[str, Any]]:
                List of parameter dictionaries representing best solutions
        """


        self._init_optimization(strategy_context)

        total_klines = len(self.market_data['klines'])
        min_klines_needed = (
            self.config.train_window_klines +
            self.config.validation_window_klines
        )

        if total_klines < min_klines_needed:
            self.logger.error(
                'Insufficient data for Walk-Forward Analysis.'
                'Aborting optimization.'
            )
            return []

        windows = create_walkforward_windows(self.market_data, self.config)

        if len(windows) < self.config.min_windows:
            self.logger.error(
                'Insufficient windows for Walk-Forward Analysis. '
                'Aborting optimization.'
            )
            return []

        all_results = []
        for _ in range(self.config.optimization_runs):
            result = self._run_single_optimization(windows)

            if result:
                all_results.append(result)

        if all_results:
            all_results.sort(
                key=lambda x: x['fitness'] + x['stability_score'],
                reverse=True
            )
            return [result['params'] for result in all_results]

        return []

    def _init_optimization(self, strategy_context: dict[str, Any]) -> None:
        """
        Prepare optimization for a specific strategy context.

        Extracts strategy class, client, market data, and
        parameter space for subsequent optimization routines.

        Args:
            strategy_context: Strategy context dictionary
        """

        self.strategy_context = strategy_context
        self.strategy = strategy_context['type']
        self.client = strategy_context['client']
        self.market_data = strategy_context['market_data']

        self.param_keys = list(self.strategy.opt_params.keys())
        self.param_space = self.strategy.opt_params

    def _run_single_optimization(
        self,
        windows: list[dict[str, int]]
    ) -> dict[str, Any] | None:
        """
        Execute one complete optimization run using Walk-Forward Analysis.

        Evolves population across generations, applies early stopping
        and convergence checks, and evaluates the best candidate.

        Args:
            windows: List of training/validation windows

        Returns:
            dict | None: Best result with metrics, or None if failed
        """

        population = self._initialize_smart_population()

        best_fitness_history = []
        generations_without_improvement = 0
        generation = 0

        current_mutation_rate = self.config.base_mutation_rate
        best_candidate = None

        while generation < self.config.max_iterations:
            print(generation)

            fitness_scores = self._evaluate_population_walkforward(
                population=population,
                windows=windows
            )

            if not fitness_scores:
                break

            population_with_fitness = list(zip(population, fitness_scores))
            population_with_fitness.sort(key=lambda x: x[1], reverse=True)

            current_best_fitness = population_with_fitness[0][1]
            best_fitness_history.append(current_best_fitness)
            best_candidate = population_with_fitness[0]

            has_converged = self._check_convergence(best_fitness_history)
            min_iterations_reached = generation >= self.config.min_iterations
            patience_exceeded = (
                generations_without_improvement >=
                self.config.convergence_patience
            )

            if has_converged:
                generations_without_improvement += 1

                if min_iterations_reached and patience_exceeded:
                    break
            else:
                generations_without_improvement = 0

            current_mutation_rate *= self.config.mutation_decay
            population = self._create_next_generation(
                population_with_fitness=population_with_fitness,
                mutation_rate=current_mutation_rate
            )
            generation += 1

        if best_candidate is None:
            return None

        best_params, best_fitness = best_candidate
        stability_score = self._get_stability_score(best_params, windows)

        return {
            'params': best_params,
            'fitness': best_fitness,
            'stability_score': stability_score
        }

    def _initialize_smart_population(self) -> list[dict[str, Any]]:
        """
        Create initial population of candidate parameter sets.

        Combines random sampling, Latin Hypercube Sampling, and
        extreme values to improve diversity and convergence speed.

        Returns:
            list[dict[str, Any]]: Population of parameter dictionaries
        """

        population = []

        random_count = int(self.config.population_size * 0.3)
        for _ in range(random_count):
            population.append({
                p: random.choice(v) for p, v in self.param_space.items()
            })

        lhs_count = int(self.config.population_size * 0.4)
        population.extend(
            latin_hypercube_sampling(self.param_space, lhs_count)
        )

        extreme_count = int(self.config.population_size * 0.2)
        for _ in range(extreme_count):
            individual = {
                p: random.choice([v[0], v[-1]])
                for p, v in self.param_space.items()
            }
            population.append(individual)

        while len(population) < self.config.population_size:
            population.append({
                p: random.choice(v) for p, v in self.param_space.items()
            })

        return population

    def _evaluate_population_walkforward(
        self,
        population: list[dict[str, Any]],
        windows: list[dict[str, int]]
    ) -> list[float]:
        """
        Evaluate entire population across Walk-Forward windows.

        Computes train and validation scores for each individual,
        applies overfitting penalty and stability penalty,
        and returns aggregated fitness scores.

        Args:
            population: Candidate parameter sets
            windows: Training/validation windows

        Returns:
            list[float]: Fitness scores for each candidate
        """

        fitness_scores = []
    
        for individual in population:
            window_scores = []
            train_scores = []
            val_scores = []

            for window in windows:
                train_data = create_window_data(
                    market_data=self.market_data,
                    window=window,
                    data_type='train'
                )
                val_data = create_window_data(
                    market_data=self.market_data,
                    window=window,
                    data_type='validation'
                )

                train_score = self._evaluate_individual(
                    params=individual,
                    market_data=train_data
                )
                val_score = self._evaluate_individual(
                    params=individual,
                    market_data=val_data
                )

                train_scores.append(train_score)
                val_scores.append(val_score)
                window_scores.append(0.3 * train_score + 0.7 * val_score)

            if not window_scores:
                fitness_scores.append(float('-inf'))
                continue

            valid_scores = [
                score for score in window_scores 
                if not (np.isnan(score) or np.isinf(score))
            ]
            
            if not valid_scores:
                fitness_scores.append(float('-inf'))
                continue

            avg_score = np.mean(valid_scores)
            score_std = np.std(valid_scores) if len(valid_scores) > 1 else 0

        if train_scores and val_scores:
            avg_train = np.mean(train_scores)
            avg_val = np.mean(val_scores)
            
            if avg_train > 0 and avg_val > 0:
                overfitting_ratio = avg_train / avg_val
                if overfitting_ratio > 1.2:
                    avg_score -= (
                        (overfitting_ratio - 1.0) *
                        self.config.overfitting_penalty * 2
                    )
            elif avg_train <= 0 or avg_val <= 0:
                avg_score = float('-inf')

            final_score = avg_score - score_std * self.config.stability_weight
            fitness_scores.append(final_score)

        return fitness_scores

    def _evaluate_individual(
        self,
        params: dict[str, Any],
        market_data: dict[str, Any]
    ) -> float:
        """
        Evaluate strategy performance with given parameters.

        Instantiates strategy with provided parameter dictionary,
        runs calculation on market data, and computes fitness
        score based on completed deals performance.

        Args:
            params: Parameter dictionary to evaluate
            market_data: Dataset to evaluate against

        Returns:
            float: Fitness score (performance metric)
        """

        try:
            instance = self.strategy(params)
            instance.calculate(market_data)

            if len(instance.completed_deals_log) > 0:
                return float(instance.completed_deals_log[:, 8].sum())
            
            return float('-inf')
        except Exception:
            return float('-inf')

    def _check_convergence(self, fitness_history: list[float]) -> bool:
        """
        Check whether population fitness has converged.

        Uses last 10 fitness values to determine if performance
        improvement is below a defined threshold.

        Args:
            fitness_history: Sequence of best fitness values

        Returns:
            bool: True if convergence detected, False otherwise
        """

        if len(fitness_history) < 10:
            return False
        
        recent_scores = fitness_history[-10:]
        convergence_threshold = self.config.convergence_threshold
        return max(recent_scores) - min(recent_scores) < convergence_threshold

    def _create_next_generation(
        self,
        population_with_fitness: list[tuple[dict[str, Any], float]],
        mutation_rate: float
    ) -> list[dict[str, Any]]:
        """
        Create the next generation of candidate solutions.

        Applies elitism, tournament selection, adaptive crossover,
        and adaptive mutation to evolve the population.

        Args:
            population_with_fitness: Current population with fitness scores
            mutation_rate: Mutation rate for adaptive mutation

        Returns:
            list[dict[str, Any]]: New population of candidate parameter sets
        """

        elite_count = max(
            1, int(len(population_with_fitness) * self.config.elite_ratio)
        )
        next_population = [
            ind for ind, _ in population_with_fitness[:elite_count]
        ]

        while len(next_population) < self.config.population_size:
            parent1 = self._tournament_selection(population_with_fitness)
            parent2 = self._tournament_selection(population_with_fitness)

            child1, child2 = self._adaptive_crossover(parent1, parent2)
            child1 = self._adaptive_mutation(child1, mutation_rate)
            child2 = self._adaptive_mutation(child2, mutation_rate)

            next_population.extend([child1, child2])

        return next_population[:self.config.population_size]

    def _tournament_selection(
        self,
        population_with_fitness: list[tuple[dict[str, Any], float]]
    ) -> dict[str, Any]:
        """
        Select one parent using tournament selection.

        Randomly samples a subset of individuals, and returns the fittest.

        Args:
            population_with_fitness: Population with fitness scores

        Returns:
            dict[str, Any]: Selected parent parameter dictionary
        """

        tournament_size = min(
            self.config.tournament_size, len(population_with_fitness)
        )
        tournament = random.sample(population_with_fitness, tournament_size)
        winner = max(tournament, key=lambda x: x[1])
        return winner[0]

    def _adaptive_crossover(
        self,
        parent1: dict[str, Any],
        parent2: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        Perform adaptive crossover between two parents.

        Swaps parameter values randomly between parents to produce offspring.

        Args:
            parent1: First parent parameters
            parent2: Second parent parameters

        Returns:
            tuple[dict[str, Any], dict[str, Any]]:
                Two offspring parameter dictionaries
        """

        child1, child2 = parent1.copy(), parent2.copy()

        for param in self.param_keys:
            if random.random() < 0.5:
                child1[param], child2[param] = child2[param], child1[param]
        
        return child1, child2

    def _adaptive_mutation(
        self,
        individual: dict[str, Any],
        mutation_rate: float
    ) -> dict[str, Any]:
        """
        Apply adaptive mutation to an individual.

        Perturbs parameter values using Gaussian-like shifts in index space,
        with fallback to random choice if invalid.

        Args:
            individual: Candidate parameter set
            mutation_rate: Probability of mutating each parameter

        Returns:
            dict[str, Any]: Mutated individual
        """
        
        mutated = individual.copy()

        for param in self.param_keys:
            if random.random() < mutation_rate:
                values = self.param_space[param]
                current_value = individual[param]

                try:
                    idx = values.index(current_value)
                    std_dev = max(1, len(values) * 0.2)
                    new_index = int(np.random.normal(idx, std_dev))
                    new_index = max(0, min(len(values) - 1, new_index))
                    mutated[param] = values[new_index]
                except (ValueError, IndexError):
                    mutated[param] = random.choice(values)
        
        return mutated

    def _get_stability_score(
        self,
        best_params: dict[str, Any],
        windows: list[dict[str, int]]
    ) -> float:
        """
        Calculate stability score for the best parameters across all windows.

        Args:
            best_params: Parameter dictionary of best candidate
            windows: Training/validation windows

        Returns:
            float: stability_score metrics
        """

        train_scores, validation_scores = [], []
        stability_score = 0.0

        for window in windows:
            train_data = create_window_data(
                market_data=self.market_data,
                window=window,
                data_type='train'
            )
            val_data = create_window_data(
                market_data=self.market_data,
                window=window,
                data_type='validation'
            )

            train_scores.append(
                self._evaluate_individual(best_params, train_data)
            )
            validation_scores.append(
                self._evaluate_individual(best_params, val_data)
            )

        if train_scores and validation_scores:
            train_std = (
                float(np.std(train_scores))
                if len(train_scores) > 1
                else 0.0
            )
            val_std = (
                float(np.std(validation_scores))
                if len(validation_scores) > 1
                else 0.0
            )
            stability_score = 1.0 / (1.0 + train_std + val_std)

        return stability_score

    def _save_params(self) -> None:
        """
        Save optimized parameters to strategy JSON files.

        Preserves existing optimization results while adding new ones.
        Files are organized by exchange/symbol/interval structure
        and stored in strategy-specific optimization directories.
        """

        for context in self.strategy_contexts.values():
            if not context.get('best_params'):
                continue

            filename = (
                f'{context['client'].exchange_name}_'
                f'{context['market_data']['symbol']}_'
                f'{context['market_data']['interval']}.json'
            )
            file_path = os.path.abspath(
                os.path.join(
                    'src',
                    'core',
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
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        existing_items = json.load(file)
                except (json.JSONDecodeError, IOError):
                    pass

            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(existing_items + new_items, file, indent=4)