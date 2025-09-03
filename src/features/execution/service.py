from __future__ import annotations
from logging import getLogger
from queue import Queue
from threading import Event, RLock, Thread
from typing import TYPE_CHECKING

from .builder import ExecutionContextBuilder
from .daemon import ExecutionDaemon
from .models import ContextStatus

if TYPE_CHECKING:
    from .models import AlertData, ContextConfig, StrategyContext


logger = getLogger(__name__)


class ExecutionService:
    """
    Unified service for trading strategy execution and analysis.
    
    Combines real-time execution with backtesting capabilities.
    
    Features:
    - Real-time strategy execution with daemon monitoring
    - Historical backtesting with performance metrics
    - Alert management and notification system
    """
    
    def __init__(self) -> None:
        """Initialize the execution service with required components."""

        self._contexts: dict[str, StrategyContext] = {}
        self._context_statuses: dict[str, ContextStatus] = {}
        self._alerts: list[AlertData] = []

        self._contexts_lock = RLock()
        self._statuses_lock = RLock()
        self._alerts_lock = RLock()
        
        self._context_builder = ExecutionContextBuilder()
        self._execution_daemon = ExecutionDaemon(self._alerts)

        self._queue: Queue[tuple[str, ContextConfig]] = Queue()
        self._pause_event = Event()
        self._monitor_thread = Thread(
            target=self._run_monitor_queue,
            daemon=True
        )
        self._monitor_thread.start()
    
    @property
    def contexts(self) -> dict[str, StrategyContext]:
        """Return a copy of all strategy contexts."""

        with self._contexts_lock:
            return self._contexts.copy()
    
    @property
    def statuses(self) -> dict[str, ContextStatus]:
        """Return a copy of all context statuses."""

        with self._statuses_lock:
            return self._context_statuses.copy()
    
    @property
    def alerts(self) -> dict[str, AlertData]:
        """Return a copy of all active alerts."""

        with self._alerts_lock:
            return self._alerts.copy()
    
    def add_contexts(self, configs: dict[str, ContextConfig]) -> list[str]:
        """
        Add new strategy contexts to the processing queue.

        - Skips contexts that already exist in contexts or statuses.
        - Marks accepted contexts as QUEUED.
        - Returns identifiers of successfully queued contexts.

        Args:
            configs: Mapping from context_id to configuration

        Returns:
            list[str]: List of successfully queued context identifiers
        """

        if not configs:
            logger.warning('No configs provided for queueing')
            return []

        added: list[str] = []
        for context_id, config in configs.items():
            with self._contexts_lock, self._statuses_lock:
                if context_id in self._contexts:
                    continue

                self._context_statuses[context_id] = ContextStatus.QUEUED
                self._queue.put((context_id, config))
                added.append(context_id)

        if added:
            self._pause_event.set()

        return added
    
    def get_context(self, context_id: str) -> StrategyContext:
        """
        Retrieve a strategy context by its identifier.
        
        Args:
            context_id: Unique context identifier
            
        Returns:
            StrategyContext: The requested strategy context
            
        Raises:
            KeyError: If context doesn't exist
        """

        with self._contexts_lock:
            if context_id not in self._contexts:
                raise KeyError(f'Context {context_id} not found')
            
            return self._contexts[context_id]

    def update_context(
        self,
        context_id: str,
        param_name: str,
        param_value: bool | int | float
    ) -> None:
        """
        Update a parameter in a strategy context and recompute metrics.

        Args:
            context_id: Unique identifier of the strategy context
            param_name: Strategy parameter name
            param_value: New parameter value

        Raises:
            KeyError: If context doesn't exist
            Exception: If updating the context fails
        """

        with self._contexts_lock:
            if context_id not in self._contexts:
                raise KeyError(f'Context {context_id} not found')
        
            context = self._contexts[context_id]

        try:
            updated_context = self._context_builder.update(
                context, param_name, param_value
            )
            with self._contexts_lock:
                self._contexts[context_id] = updated_context
        except Exception as e:
            logger.error(
                f'Failed to update context {context_id}: '
                f'{type(e).__name__} - {e}'
            )
            raise
    
    def delete_context(self, context_id: str) -> None:
        """
        Delete a strategy context and stop monitoring if necessary.
        
        Args:
            context_id: Unique context identifier
        
        Raises:
            KeyError: If context doesn't exist
            Exception: If deleting the context fails
        """

        with self._contexts_lock:
            if context_id not in self._contexts:
                raise KeyError(f'Context {context_id} not found')
        
            context = self._contexts[context_id]

        try:
            if context['is_live']:
                self._execution_daemon.remove_context(context_id)

            with self._contexts_lock:
                del self._contexts[context_id]

            with self._statuses_lock:
                self._context_statuses.pop(context_id, None)
        except Exception as e:
            logger.error(
                f'Failed to delete context {context_id}: '
                f'{type(e).__name__} - {e}'
            )
            raise
    
    def get_context_status(self, context_id: str) -> ContextStatus:
        """
        Get current status for a specific strategy context.
        
        Args:
            context_id: Unique context identifier
            
        Returns:
            ContextStatus: Current context status
        
        Raises:
            KeyError: If context doesn't exist
        """

        with self._contexts_lock:
            if context_id not in self._contexts:
                raise KeyError(f'Context {context_id} not found')

        with self._statuses_lock:
            return self._context_statuses.get(context_id)
    
    def delete_alert(self, alert_id: str) -> None:
        """
        Remove an alert from the active alerts collection.
        
        Args:
            alert_id: Unique identifier of the alert
            
        Raises:
            KeyError: If alert doesn't exist
        """

        with self._alerts_lock:
            for i, alert in enumerate(self._alerts):
                if alert['alert_id'] == alert_id:
                    del self._alerts[i]
                    return

            raise KeyError(f'Alert {alert_id} not found')

    def _run_monitor_queue(self) -> None:
        """
        Background monitor loop for processing queued context creations.

        - Waits when queue is empty.
        - Wakes up when new contexts are queued via add_contexts.
        - Sequentially creates each context via _create_context.
        """

        while True:
            if self._queue.empty():
                self._pause_event.clear()
                self._pause_event.wait()

            context_id, config = self._queue.get()
            self._create_context(context_id, config)

    def _create_context(self, context_id: str, config: ContextConfig) -> None:
        """
        Create a single strategy context and update its lifecycle status.

        Steps:
          - Set status to CREATING
          - Build context via ExecutionContextBuilder
          - Attach to daemon if live
          - On success: store context and set status to CREATED
          - On failure: set status to FAILED and log error

        Args:
            context_id: Unique identifier for the strategy context
            config: Configuration of the context
        """

        self._set_status(context_id, ContextStatus.CREATING)

        try:
            context = self._context_builder.create(config)

            if config['is_live']:
                self._execution_daemon.add_context(context_id, context)

            with self._contexts_lock:
                self._contexts[context_id] = context

            self._set_status(context_id, ContextStatus.READY)
        except Exception as e:
            self._set_status(context_id, ContextStatus.FAILED)
            logger.error(
                f'Failed to create context {context_id}: '
                f'{type(e).__name__} - {e}'
            )
    
    def _set_status(self, context_id: str, status: ContextStatus) -> None:
        """Update context status."""

        with self._statuses_lock:
            self._context_statuses[context_id] = status