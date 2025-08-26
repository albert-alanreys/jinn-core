from dataclasses import dataclass


@dataclass
class OptimizationConfig:
    # Optimization parameters
    iterations: int = 1000
    optimization_runs: int = 3
    
    # Population parameters
    population_size: float = 200
    max_population_size: float = 250
    
    # Data splitting parameters
    train_window: float = 0.7
    test_window: float = 0.3


CONFIG = OptimizationConfig()