from dataclasses import dataclass
from os import cpu_count


@dataclass
class OptimizationConfig:
    # Advanced GA parameters
    convergence_patience: int = 8
    convergence_threshold: float = 0.5
    elite_ratio: float = 0.30

    # Core optimization parameters
    max_iterations: int = 50
    max_population_size: int = 100
    max_processes: int = cpu_count()
    min_iterations: int = 20
    population_size: int = 50

    # Mutation and crossover parameters
    base_mutation_rate: float = 0.20
    mutation_decay: float = 0.90
    tournament_size: int = 4

    # Stability and risk parameters
    optimization_runs: int = 1
    overfitting_penalty: float = 0.3
    stability_weight: float = 0.1

    # Walk-Forward Analysis parameters
    min_windows: int = 3
    step_klines: int = 200
    train_window_klines: int = 3000
    validation_window_klines: int = 1000


CONFIG = OptimizationConfig()