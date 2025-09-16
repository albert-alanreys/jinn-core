from __future__ import annotations
from logging import getLogger
from threading import Event, RLock, Thread
from time import sleep
from typing import TYPE_CHECKING
from uuid import uuid4

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

    _ALERTS_LIMIT = 1000
    _MONITOR_INTERVAL = 1.0
    
    def __init__(self, alerts: list[AlertData]) -> None:
        """
        Initialize the execution daemon.
        
        Args:
            alerts: Shared alert storage
        """

        self._contexts: dict[str, StrategyContext] = {}
        self._alerts = alerts

        self._realtime_provider = RealtimeProvider()
        self._telegram_client = TelegramClient()
        self._strategy_tester = StrategyTester()

        self._context_lock = RLock()

        self._pause_event = Event()
        self._pause_event.clear()

        self._daemon_thread = Thread(
            target=self._run_monitoring_loop,
            daemon=True
        )
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
            self._pause_event.set()
    
    def remove_context(self, context_id: str) -> bool:
        """
        Remove strategy context from daemon monitoring.
        
        Args:
            context_id: Unique identifier for the strategy context
            
        Returns:
            True if context was removed, False if not found
        """

        with self._context_lock:
            if context_id in self._contexts:
                del self._contexts[context_id]

                if len(self._contexts) == 0:
                    self._pause_event.clear()
                
                return True
        
        return False

    def _run_monitoring_loop(self) -> None:
        """
        Continuous background loop for monitoring strategy contexts.

        - Waits until _pause_event is set.
        - Processes all contexts and cleans up alerts.
        - Sleeps for configured interval between cycles.
        - Never exits during normal operation (runs as daemon thread).
        """

        while True:
            self._pause_event.wait()

            try:
                self._process_all_contexts()
                self._cleanup_old_alerts()
                sleep(self._MONITOR_INTERVAL)
            except Exception:
                logger.exception('Error in daemon monitoring loop')
    
    def _process_all_contexts(self) -> None:
        """Process all monitored strategy contexts for updates."""

        with self._context_lock:
            context_items = list(self._contexts.items())

        if not context_items:
            return
        
        for context_id, context in context_items:
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

        metrics = self._strategy_tester.test(strategy, context['market_data'])
        context['metrics'] = metrics

        for client in  context['clients']:
            strategy.__trade__(client)
    
    def _process_alerts(
        self,
        context_id: str,
        context: StrategyContext,
    ) -> None:
        """
        Process trading alerts by storing them in the registry
        and sending via Telegram.
        
        Args:
            context_id: Strategy context identifier
            context: Strategy execution context
        """

        all_alerts = []
        for client in context['clients']:
            alerts = client.trade.alerts
            if alerts:
                all_alerts.extend(alerts.copy())
                alerts.clear()

        if not all_alerts:
            return

        for alert in all_alerts:
            self._alerts.append({
                'alert_id': str(uuid4()),
                'context_id': context_id,
                **alert,
            })

            try:
                self._telegram_client.send_order_alert(alert)
            except Exception as e:
                logger.warning(
                    f'Failed to send Telegram alert for {context_id}: {e}'
                )

    def _cleanup_old_alerts(self) -> None:
        """Remove oldest alerts if registry exceeds the limit."""

        excess = len(self._alerts) - self._ALERTS_LIMIT
        if excess > 0:
            self._alerts = self._alerts[excess:]