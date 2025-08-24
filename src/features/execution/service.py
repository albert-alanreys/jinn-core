from __future__ import annotations
from logging import getLogger
from threading import RLock, Thread
from typing import Any, TYPE_CHECKING

from .builder import StrategyContextBuilder
from .daemon import ExecutionDaemon

if TYPE_CHECKING:
    from .models import (
        AlertData,
        ContextConfig,
        ContextStatus,
        StrategyContext
    )


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

        # Core storage
        self._contexts: dict[str, StrategyContext] = {}
        self._context_statuses: dict[str, ContextStatus] = {}
        self._alerts: dict[str, AlertData] = {}

        # Locks for thread-safe access
        self._contexts_lock = RLock()
        self._statuses_lock = RLock()
        self._alerts_lock = RLock()
        
        # Service components
        self._context_builder = StrategyContextBuilder()
        self._execution_daemon = ExecutionDaemon(self._alerts)
        
        logger.info('ExecutionService initialized successfully')
    
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
    
    def create_contexts(self, configs: dict[str, ContextConfig]) -> None:
        """
        Create multiple strategy contexts asynchronously.
        
        Spawns a background thread that builds contexts, updates statuses,
        and registers live contexts in the execution daemon.

        Args:
            configs: Mapping from context_id to configuration
        """

        if not configs:
            logger.warning('No configurations provided for context creation')
            return
        
        creation_thread = Thread(
            target=self._create_contexts,
            args=(configs,),
            daemon=True
        )
        creation_thread.start()
    
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
        param_value: Any
    ) -> bool:
        """
        Update a parameter in a strategy context and recompute its metrics.

        Args:
            context_id: Unique identifier of the strategy context
            param_name: Strategy parameter name
            param_value: New parameter value

        Returns:
            bool: True if the context was updated successfully

        Raises:
            KeyError: If context doesn't exist
            Exception: Raised if updating the context fails
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
            
            return True
        except Exception as e:
            logger.error(
                f'Failed to update context {context_id}: '
                f'{type(e).__name__} - {e}'
            )
            raise
    
    def delete_context(self, context_id: str) -> bool:
        """
        Delete a strategy context and stop monitoring if necessary.
        
        Args:
            context_id: Unique context identifier
            
        Returns:
            bool: True if context was deleted successfully
            
        Raises:
            KeyError: If context doesn't exist
            Exception: Raised if deleting the context fails
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
    
    def get_contexts_status(self) -> dict[str, ContextStatus]:
        """
        Get current status for all strategy contexts.
        
        Returns:
            dict: Mapping of context IDs to their statuses
        """

        with self._statuses_lock:
            return self._context_statuses.copy()
    
    def get_context_status(self, context_id: str) -> ContextStatus:
        """
        Get current status for a specific strategy context.
        
        Args:
            context_id: Unique context identifier
            
        Returns:
            ContextStatus: Current context status
        """

        with self._statuses_lock:
            return self._context_statuses.get(context_id)
    
    def delete_alert(self, alert_id: str) -> bool:
        """
        Remove an alert from the active alerts collection.
        
        Args:
            alert_id: Unique identifier of the alert
            
        Returns:
            bool: True if the alert was deleted successfully
            
        Raises:
            KeyError: If alert doesn't exist
        """

        with self._alerts_lock:
            if alert_id not in self._alerts:
                raise KeyError(f'Alert {alert_id} not found')
            
            del self._alerts[alert_id]
    
    def _create_contexts(
        self,
        configs: dict[str, ContextConfig],
    ) -> dict[str, bool]:
        """
        Build strategy contexts in the background thread.

        For each context:
          - set status to CREATING
          - build context via StrategyContextBuilder
          - attach to daemon if live
          - set final status to CREATED or FAILED
          - store in shared state on success
        
        Args:
            configs: Context configurations
        """

        self._init_statuses_as_creating(configs)

        for context_id, config in configs.items():
            try:
                context = self._context_builder.create(config)

                if config['is_live']:
                    self._execution_daemon.add_context(context_id, context)

                with self._contexts_lock:
                    self._contexts[context_id] = context

                self._set_status(context_id, ContextStatus.CREATED)
            except Exception as e:
                self._set_status(context_id, ContextStatus.FAILED)
                logger.error(
                    f'Failed to create context {context_id}: '
                    f'{type(e).__name__} - {e}'
                )

    def _init_statuses_as_creating(
        self,
        configs: dict[str, ContextConfig],
    ) -> None:
        """Initialize all context statuses with CREATING state."""

        with self._statuses_lock:
            for context_id in configs:
                self._context_statuses[context_id] = ContextStatus.CREATING
    
    def _set_status(self, context_id: str, status: ContextStatus) -> None:
        """Update context status."""

        with self._statuses_lock:
            self._context_statuses[context_id] = status