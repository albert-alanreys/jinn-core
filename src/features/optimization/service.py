from __future__ import annotations
from logging import getLogger
from os import cpu_count, getenv
from queue import Queue, Empty
from threading import Event, RLock, Thread
from typing import TYPE_CHECKING
from multiprocessing import Process, Queue as MPQueue

from .builder import OptimizationContextBuilder
from .models import ContextStatus
from .optimizer import optimize_worker

if TYPE_CHECKING:
    from .models import ContextConfig, StrategyContext


logger = getLogger(__name__)


class OptimizationService:
    """
    Service for managing strategy optimization contexts in separate processes.
    
    Handles context creation, optimization execution via genetic algorithms,
    and result collection. Uses multi-threading for queue processing and 
    multi-processing for CPU-intensive optimization tasks.
    """

    def __init__(self) -> None:
        """Initialize the optimization service with required components."""

        self._contexts: dict[str, StrategyContext] = {}
        self._context_statuses: dict[str, ContextStatus] = {}

        self._contexts_lock = RLock()
        self._statuses_lock = RLock()
        
        self._context_builder = OptimizationContextBuilder()

        self._config_queue: Queue[tuple[str, ContextConfig]] = Queue()
        self._optimization_queue: Queue[tuple[str, ContextConfig]] = Queue()

        self._config_event = Event()
        self._opt_event = Event()
        self._proc_event = Event()

        self._mp_results_queue: MPQueue[
            tuple[str, list[dict] | None, str | None]
        ] = MPQueue()
        self._active_procs: dict[str, Process] = {}
        self._active_lock = RLock()

        max_processes_env = getenv('MAX_PROCESSES')
        if max_processes_env and max_processes_env.strip():
            self._max_processes = int(max_processes_env)
        else:
            self._max_processes = cpu_count()

        self._config_thread = Thread(
            target=self._run_monitor_config_queue,
            daemon=True
        )
        self._config_thread.start()

        self._opt_thread = Thread(
            target=self._run_monitor_optimization_queue,
            daemon=True
        )
        self._opt_thread.start()

        self._results_thread = Thread(
            target=self._listen_results,
            daemon=True
        )
        self._results_thread.start()
    
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
                self._config_queue.put((context_id, config))
                added.append(context_id)

        if added:
            self._config_event.set()

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
    
    def delete_context(self, context_id: str) -> None:
        """
        Delete a strategy context and terminate associated processes.
        
        Args:
            context_id: Unique context identifier
            
        Raises:
            KeyError: If context doesn't exist
            Exception: If deleting the context fails
        """

        with self._contexts_lock:
            if context_id not in self._contexts:
                raise KeyError(f'Context {context_id} not found')

        try:
            with self._contexts_lock:
                del self._contexts[context_id]

            with self._statuses_lock:
                self._context_statuses.pop(context_id, None)

            with self._active_lock:
                proc = self._active_procs.pop(context_id, None)
            
            if proc is not None and proc.is_alive():
                try:
                    proc.terminate()
                    proc.join(timeout=1.0)
                except Exception:
                    logger.exception(
                        f'Failed to terminate process for {context_id}', 
                    )
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
            KeyError: If the context status doesn't exist
        """

        with self._contexts_lock:
            status = self._context_statuses.get(context_id)
            
            if status is None:
                raise KeyError(f'Context status for {context_id} not found')
            
            return status
    
    def _run_monitor_config_queue(self) -> None:
        while True:
            if self._config_queue.empty():
                self._config_event.clear()
                self._config_event.wait()

            try:
                context_id, config = self._config_queue.get(timeout=0.5)
            except Empty:
                continue

            self._set_status(context_id, ContextStatus.CREATING)

            try:
                context = self._context_builder.create(config)
                with self._contexts_lock:
                    self._contexts[context_id] = context

                self._optimization_queue.put((context_id, context))
                self._opt_event.set()
            except Exception as e:
                self._set_status(context_id, ContextStatus.FAILED)
                logger.error(
                    f'Failed to create context {context_id}: '
                    f'{type(e).__name__} - {e}'
                )

    def _run_monitor_optimization_queue(self) -> None:
        while True:
            if self._optimization_queue.empty():
                self._opt_event.clear()
                self._opt_event.wait()

            try:
                context_id, context = (
                    self._optimization_queue.get(timeout=1.0)
                )
            except Empty:
                continue

            while True:
                with self._active_lock:
                    active_count = len(self._active_procs)
                
                if active_count < self._max_processes:
                    break

                self._proc_event.clear()
                self._proc_event.wait(timeout=1.0)

            proc = Process(
                target=optimize_worker,
                args=(context_id, context, self._mp_results_queue),
                daemon=True
            )
            proc.start()

            with self._active_lock:
                self._active_procs[context_id] = proc

    def _listen_results(self) -> None:
        while True:
            try:
                context_id, params, error = self._mp_results_queue.get()
            except Exception:
                continue

            with self._contexts_lock:
                if context_id not in self._contexts:
                    context = None
                else:
                    context = self._contexts[context_id]
                    if params is not None:
                        context['optimized_params'] = params

            if context is not None:
                if error is None:
                    self._set_status(context_id, ContextStatus.READY)
                else:
                    self._set_status(context_id, ContextStatus.FAILED)
                    logger.error(
                        f'Optimization failed for {context_id}: {error}'
                    )

            with self._active_lock:
                proc = self._active_procs.pop(context_id, None)

            if proc is not None:
                try:
                    proc.join(timeout=1.0)
                except Exception:
                    logger.exception(f'Join failed for {context_id}')

            self._proc_event.set()

    def _set_status(self, context_id: str, status: ContextStatus) -> None:
        """Update context status."""

        with self._statuses_lock:
            self._context_statuses[context_id] = status