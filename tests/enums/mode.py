from __future__ import annotations
from enum import Enum


class Mode(Enum):
    """
    Strategy testing execution modes.
    
    Defines available testing methodologies for strategy validation.
    """

    BACKTESTING = 'backtesting'
    OPTIMIZATION = 'optimization'
    FULL_PIPELINE = 'full_pipeline'

    @classmethod
    def from_short(cls, short: str) -> Mode:
        """
        Convert single-character abbreviation to Mode enum.
        
        Provides quick command-line interface for test mode selection
        using intuitive single-letter mappings.
        
        Args:
            short: Single character abbreviation:
                'b' - backtesting
                'o' - optimization
                'f' - full pipeline
        
        Returns:
            Corresponding Mode enum value
        
        Raises:
            ValueError: If provided abbreviation doesn't match any known mode
        """
        
        mapping = {mode.name[0].lower(): mode for mode in cls}

        if short.lower() not in mapping:
            raise ValueError(f'Unknown test mode: {short}')

        return mapping[short.lower()]