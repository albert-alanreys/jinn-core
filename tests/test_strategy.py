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
    def test_backtesting(
        self,
        execution_service,
        backtesting_config
    ) -> None:
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
        added = service.add_contexts({str(uuid4()): config})
        if not added:
            raise RuntimeError('Failed to create context for test')
        
        context_id = added[0]

        while True:
            try:
                status = service.get_context_status(context_id)
                if status in statuses:
                    return context_id
            except KeyError:
                pass

            sleep(1)