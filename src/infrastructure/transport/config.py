from dataclasses import dataclass, field


@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    
    max_attempts: int = 3
    delay_between_attempts: float = 1.0


@dataclass
class TimeoutConfig:
    """Timeout configuration."""
    
    connect_timeout: float = 5.0
    read_timeout: float = 30.0
    
    @property
    def as_tuple(self) -> tuple[float, float]:
        """Returns timeouts as a tuple for requests."""

        return (self.connect_timeout, self.read_timeout)


@dataclass
class TransportConfig:
    """Basic configuration of the transport layer."""
    
    retry: RetryConfig = field(default_factory=RetryConfig)
    timeout: TimeoutConfig = field(default_factory=TimeoutConfig)
    logging_enabled: bool = True


DEFAULT_CONFIG = TransportConfig()