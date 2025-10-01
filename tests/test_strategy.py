from __future__ import annotations
from time import sleep
from uuid import uuid4

from src.features.execution.models import (
    ContextStatus as ExecutionContextStatus
)
from src.features.optimization.models import (
    ContextStatus as OptimizationContextStatus
)


class TestStrategy:
    """Test trading strategy execution and optimization workflows."""
    
    def test_backtesting(
        self,
        execution_service,
        backtesting_config
    ) -> None:
        """
        Test strategy backtesting functionality.
        
        Validates that an execution context can be created and
        successfully transitions to READY status without failures.
        
        Args:
            execution_service: Service for strategy execution
            backtesting_config: Configuration for backtesting context
        """

        context_id = self._create_context(
            service=execution_service,
            config=backtesting_config,
            statuses=[
                ExecutionContextStatus.FAILED,
                ExecutionContextStatus.READY
            ]
        )

        status = execution_service.get_context_status(context_id)
        assert status != ExecutionContextStatus.FAILED
        assert status == ExecutionContextStatus.READY

    def test_optimization(
        self,
        optimization_service,
        optimization_config
    ) -> None:
        """
        Test strategy parameter optimization functionality.
        
        Validates that an optimization context can be created and
        successfully transitions to READY status without failures.
        
        Args:
            optimization_service: Service for strategy optimization
            optimization_config: Configuration for optimization context
        """

        context_id = self._create_context(
            service=optimization_service,
            config=optimization_config,
            statuses=[
                OptimizationContextStatus.FAILED,
                OptimizationContextStatus.READY
            ]
        )

        status = optimization_service.get_context_status(context_id)
        assert status != OptimizationContextStatus.FAILED
        assert status == OptimizationContextStatus.READY

    def test_full_pipeline(
        self,
        execution_service,
        backtesting_config,
        optimization_service,
        optimization_config
    ) -> None:
        """
        Test complete strategy workflow from backtesting to optimization.
        
        Validates end-to-end pipeline by running backtesting followed
        by optimization, ensuring both phases complete successfully.
        
        Args:
            execution_service: Service for strategy execution
            backtesting_config: Configuration for backtesting context
            optimization_service: Service for strategy optimization
            optimization_config: Configuration for optimization context
        """

        # Run backtesting phase
        context_id = self._create_context(
            service=execution_service,
            config=backtesting_config,
            statuses=[
                ExecutionContextStatus.FAILED,
                ExecutionContextStatus.READY
            ]
        )

        status = execution_service.get_context_status(context_id)
        assert status != ExecutionContextStatus.FAILED
        assert status == ExecutionContextStatus.READY

        # Run optimization phase
        context_id = self._create_context(
            service=optimization_service,
            config=optimization_config,
            statuses=[
                OptimizationContextStatus.FAILED,
                OptimizationContextStatus.READY
            ]
        )

        status = optimization_service.get_context_status(context_id)
        assert status != OptimizationContextStatus.FAILED
        assert status == OptimizationContextStatus.READY

    @staticmethod
    def _create_context(service, config, statuses) -> str:
        """
        Create a context and wait for terminal status.
        
        Polls the service until context reaches one of the specified
        terminal statuses (READY or FAILED).
        
        Args:
            service: Execution or optimization service instance
            config: Context configuration dictionary
            statuses: List of terminal statuses to wait for
            
        Returns:
            str: Created context identifier
            
        Raises:
            RuntimeError: If context creation fails
        """

        added = service.add_contexts({str(uuid4()): config})
        if not added:
            raise RuntimeError('Failed to create context for test')
        
        context_id = added[0]

        # Poll until context reaches terminal status
        while True:
            status = service.get_context_status(context_id)
            if status in statuses:
                return context_id

            sleep(1)