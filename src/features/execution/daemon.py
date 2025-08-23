from __future__ import annotations

import time
from logging import getLogger
from threading import Event, Lock, Thread
from typing import TYPE_CHECKING
from weakref import WeakKeyDictionary

from src.core.providers import RealtimeProvider
from src.infrastructure.messaging import TelegramClient
from .tester import StrategyTester

if TYPE_CHECKING:
    from .models import AlertData, StrategyContext


logger = getLogger(__name__)


class ExecutionDaemon:
    """
    Real-time strategy execution monitoring daemon.
    
    Continuously monitors live strategy contexts for market data updates,
    executes strategy calculations, and processes trading alerts in a
    separate daemon thread for non-blocking operation.
    """
    
    def __init__(self, alert_registry: dict[str, AlertData]) -> None:
        """
        Initialize the execution daemon.
        
        Args:
            alert_registry: Shared alert storage
        """

        self._contexts = WeakKeyDictionary()
        self._alert_registry = alert_registry
        
        self._realtime_provider = RealtimeProvider()
        self._telegram_client = TelegramClient()
        self._strategy_tester = StrategyTester()
        
        self._shutdown_event = Event()
        self._context_lock = Lock()
        
        self._daemon_thread = Thread(target=self._run, daemon=True)
        self._daemon_thread.start()
    
    def add_context(self, context_id: str, context: StrategyContext) -> None:
        """
        Add strategy context to daemon monitoring.
        
        Args:
            context_id: Unique identifier for the strategy context
            context: Complete strategy execution context
        """

        with self._context_lock:
            self._contexts[context_id] = context
    
    def _run(self) -> None:
        """Main daemon loop for continuous strategy monitoring."""
        
        while not self._shutdown_event.is_set():
            try:
                with self._context_lock:
                    self._process_all_contexts()
                
                time.sleep(1.0)
            except Exception:
                logger.exception('Error in daemon monitoring loop')
    
    def _process_all_contexts(self) -> None:
        """Process all monitored strategy contexts for updates."""

        for context_id, context in self._contexts.items():
            try:
                if self._realtime_provider.update_data(context):
                    self._execute_strategy(context)
                    self._process_alerts(context_id, context)
            except Exception:
                logger.exception(f'Error processing context {context_id}')
    
    def _execute_strategy(self, context: StrategyContext) -> None:
        """
        Execute strategy calculations and trading operations.
        
        Args:
            context: Strategy execution context
        """

        strategy = context['strategy']
        strategy.calculate(context['market_data'])
        strategy.trade(context['client'])
        context['metrics'] = self._strategy_tester.test(strategy)
    
    def _process_alerts(
        self,
        context_id: str,
        context: StrategyContext,
    ) -> None:
        """
        Process and distribute trading alerts.
        
        Args:
            context_id: Strategy context identifier
            context: Strategy execution context
        """

        alerts = context['client'].trade.alerts
        
        if not alerts:
            return
        
        for alert in alerts:
            alert_data = {
                'context_id': context_id,
                'strategy': context['name'],
                'message': alert.copy(),
            }
            alert_id = str(hash(f'{context_id}_{time.time()}'))
            self._alert_registry[alert_id] = alert_data

            try:
                self.telegram_client.send_order_alert(alert)
            except Exception as e:
                logger.warning(
                    f'Failed to send Telegram alert for {context_id}: {e}'
                )
        
        alerts.clear()