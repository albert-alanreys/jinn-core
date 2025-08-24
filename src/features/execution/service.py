from __future__ import annotations
from logging import getLogger
from threading import Thread
from typing import Any, TYPE_CHECKING

from .builder import ExecutionContextBuilder
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
    Comprehensive trading strategy execution and analysis service.
    
    Provides unified interface for both real-time strategy execution
    and historical performance analysis through backtesting capabilities.
    
    Key Features:
    - Real-time strategy execution with daemon-based monitoring
    - Historical backtesting with comprehensive metrics
    - Alert management and notification system
    - Thread-safe context management
    """
    
    def __init__(self) -> None:
        """Initialize the execution service with required components."""

        # Core storage
        self._contexts: dict[str, StrategyContext] = {}
        self._context_statuses: dict[str, ContextStatus] = {}
        self._alerts: dict[str, AlertData] = {}
        
        # Service components
        self._context_builder = ExecutionContextBuilder()
        self._execution_daemon = ExecutionDaemon(self._alerts)
        
        logger.info('ExecutionService initialized successfully')
    
    @property
    def contexts(self) -> dict[str, StrategyContext]:
        """Get read-only view of all strategy contexts."""

        return self._contexts.copy()
    
    @property
    def statuses(self) -> dict[str, ContextStatus]:
        """Get read-only view of all context statuses."""

        return self._context_statuses.copy()
    
    @property
    def alerts(self) -> dict[str, AlertData]:
        """Get read-only view of all alerts."""

        return self._alerts.copy()
    
    def create_contexts(self, configs: dict[str, ContextConfig]) -> None:
        """
        Start asynchronous creation of multiple strategy contexts.
        
        Args:
            configs: Dictionary mapping context IDs to their configurations
        """

        if not configs:
            logger.warning('Configurations not provided')
            return
        
        creation_thread = Thread(
            target=self._create_contexts,
            args=(configs,),
            daemon=True
        )
        creation_thread.start()

    
    
    def get_context(self, context_id: str) -> StrategyContext:
        """
        Retrieve strategy context by ID.
        
        Args:
            context_id: Unique context identifier
            
        Returns:
            StrategyContext: Strategy context
            
        Raises:
            KeyError: If context doesn't exist
        """

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
        Update parameter in strategy context and restart strategy.

        Args:
            context_id: Unique identifier of the strategy context
            param_name: strategy parameter name
            param_value: new parameter value

        Returns:
            bool: True if context was updated successfully

        Raises:
            KeyError: If context doesn't exist
        """

        if context_id not in self._contexts:
            raise KeyError(f'Context {context_id} not found')
        
        context = self._contexts[context_id]

        try:
            context = self._context_builder.update(
                context, param_name, param_value
            )
            self._contexts[context_id] = context
        except Exception as e:
            logger.error(
                f'Failed to update context {context_id}: '
                f'{type(e).__name__} - {e}'
            )
    
    def delete_context(self, context_id: str) -> bool:
        """
        Delete strategy context and stop monitoring.
        
        Args:
            context_id: Unique context identifier
            
        Returns:
            bool: True if context was deleted successfully
            
        Raises:
            KeyError: If context doesn't exist
        """

        if context_id not in self._contexts:
            raise KeyError(f'Context {context_id} not found')
        
        context = self._contexts[context_id]
        if context['is_live']:
            self._execution_daemon.remove_context(context_id)
        
        del self._contexts[context_id]
        self._context_statuses.pop(context_id, None)

        return True
    
    def get_contexts_status(self) -> dict[str, ContextStatus]:
        """
        Get current status of all strategy contexts.
        
        Returns:
            dict: Dictionary mapping context IDs to their current statuses
        """

        return self._context_statuses.copy()
    
    def get_context_status(self, context_id: str) -> ContextStatus:
        """
        Get current status of a strategy context.
        
        Args:
            context_id: Unique context identifier
            
        Returns:
            ContextStatus: Current context status
        """

        return self._context_statuses.get(context_id, ContextStatus.FAILED)
    
    def delete_alert(self, alert_id: str) -> bool:
        """
        Remove alert from active alerts collection.
        
        Args:
            alert_id: Unique identifier of the alert
            
        Returns:
            bool: True if alert was deleted successfully
            
        Raises:
            KeyError: If alert doesn't exist
        """

        if alert_id not in self._alerts:
            raise KeyError(f'Alert {alert_id} not found')
        
        del self._alerts[alert_id]
    
    def _create_contexts(
        self,
        configs: dict[str, ContextConfig],
    ) -> dict[str, bool]:
        """
        Create strategy contexts from configurations.
        
        Args:
            configs: Context configurations
        """

        self._init_statuses_as_creating(configs)

        for context_id, config in configs.items():
            try:
                context = self._context_builder.create(config)

                if config['is_live']:
                    self._execution_daemon.add_context(context_id, context)
                
                self._contexts[context_id] = context
            except Exception as e:
                self._context_statuses[context_id] = ContextStatus.FAILED

                logger.error(
                    f'Failed to create context {context_id}: '
                    f'{type(e).__name__} - {e}'
                )

        self._update_statuses_after_creation(configs)

    def _init_statuses_as_creating(
        self,
        configs: dict[str, ContextConfig],
    ) -> None:
        """Set all context statuses to CREATING before processing."""

        for context_id in configs:
            self._context_statuses[context_id] = ContextStatus.CREATING
    
    def _update_statuses_after_creation(
        self,
        configs: dict[str, ContextConfig],
    ) -> None:
        """Update statuses for successfully created contexts."""
        
        for context_id in configs:
            if self._context_statuses[context_id] == ContextStatus.CREATING:
                self._context_statuses[context_id] = ContextStatus.CREATED