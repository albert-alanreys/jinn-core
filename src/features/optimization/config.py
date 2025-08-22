from dataclasses import dataclass
from os import cpu_count


@dataclass
class OptimizationConfig:
    # Optimization parameters
    iterations: int = 1000
    optimization_runs: int = 3
    
    # Population parameters
    population_size: float = 200
    max_population_size: float = 250
    
    # Parallel processing parameters
    max_processes: int = cpu_count()
    
    # Data splitting parameters
    train_window_klines: float = 0.7
    validation_window_klines: float = 0.3


CONFIG = OptimizationConfig()