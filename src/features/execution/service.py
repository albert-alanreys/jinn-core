from logging import getLogger

from .builder import ContextBuilder
from .daemon import ExecutionDaemon
from .tester import StrategyTester


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

        self.context_builder = ContextBuilder()
        self.strategy_tester = StrategyTester()
        self.execution_daemon = ExecutionDaemon()

        self.logger = getLogger()

    def create_contexts(self, configs: dict) -> None:
        for cid in configs.keys():
            self.contexts[cid] = {'status': 'in_progress'}

        self.context_builder.build(self.contexts, configs)

        for context in self.contexts:
            try:
                self.strategy_tester.test(context)
            except Exception:
                self.logger.exception('An error occurred')
                context.update({'status': 'failed'})

        self.execution_daemon.add_contexts(self.contexts)

        for cid in configs.keys():
            if self.contexts[cid]['status'] != 'failed':
                self.contexts[cid] = {'status': 'success'}


executionService = ExecutionService()