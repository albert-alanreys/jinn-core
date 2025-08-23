from typing import TYPE_CHECKING
from logging import getLogger

from .builder import ContextBuilder
from .daemon import ExecutionDaemon


if TYPE_CHECKING:
    from .models import ContextConfig
    from .models import StrategyContext


class ExecutionService:
    """
    Comprehensive trading strategy execution and analysis service.
    
    Provides integrated capabilities for both real-time trading execution
    and historical strategy performance analysis through backtesting.
    
    Supported Capabilities:
    ----------------------
    - Real-time Strategy Execution:
      * Continuous monitoring of market data updates
      * Automated strategy calculations and signal generation
      * Live order execution and position management
      * Daemon-based operation for non-blocking performance
    
    - Strategy Performance Analysis:
      * Historical backtesting on market data
      * Comprehensive metrics calculation across four categories:
        • Overview: Equity curve analysis and summary statistics
        • Performance: Returns, efficiency ratios, and performance benchmarks
        • Trades: Trade-level analytics and execution quality metrics
        • Risk: Drawdown analysis, volatility, and risk-adjusted returns
      * Deal log processing and trade reconstruction
    """

    def __init__(self) -> None:
        self.contexts = {}
        self.statuses = {}
        self.alerts = {}

        self.context_builder = ContextBuilder()
        self.execution_daemon = ExecutionDaemon()

        self.logger = getLogger()

    def create_contexts(self, configs: dict[str, 'ContextConfig']) -> None:
        self._init_statuses(configs)

        new_contexts = self._build_contexts(configs)
        self.contexts.update(new_contexts)
        
        self._complete_statuses(new_contexts)

    def delete_context(self, context_id: str) -> bool:
        try:
            self.contexts.pop(context_id)
        except KeyError:
            raise KeyError
    
    def _init_statuses(self, configs: dict[str, 'ContextConfig']) -> None:
        # flask-сервер сможет в другом потоке проверять статус контекста
        for cid in configs.keys():
            self.statuses[cid] = 'pending'

    def _build_contexts(
        self,
        configs: dict[str, 'ContextConfig']
    ) -> dict[str, 'StrategyContext']:
        new_contexts = {}

        for cid, config in configs.items():
            try:
                context = self.context_builder.build(config)

                if config['is_live']:
                    self.execution_daemon.watch(cid, context)
                
                new_contexts[cid] = context
            except Exception:
                self.statuses[cid] = 'failed'
                self.logger.exception('An error occurred')

        return new_contexts


    def _complete_statuses(self, configs: dict[str, 'ContextConfig']) -> None:
        for cid in configs.keys():
            if cid in self.contexts:
                self.statuses[cid] = 'success'


execution_service = ExecutionService()