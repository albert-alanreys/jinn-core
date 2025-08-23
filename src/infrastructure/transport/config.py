from __future__ import annotations
from dataclasses import dataclass


@dataclass
class TransportConfig:
    """Basic configuration of the transport layer."""
    
    retry_delay: float = 1.0
    retry_attempts: int = 3
    logging: bool = True


CONFIG = TransportConfig()