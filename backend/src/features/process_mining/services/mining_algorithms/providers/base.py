"""Abstract Mining Provider Interface.

Defines the contract for mining algorithm providers.
Enables swapping PM4Py for external miners (ProM, commercial engines).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from src.features.process_mining.enums import MinerType, ModelFormat


@dataclass
class ComplexityEstimate:
    """Estimated resource requirements for mining operation."""

    estimated_memory_mb: int
    estimated_time_seconds: float
    algorithm_complexity: str  # O(n), O(n^2), O(n*m), etc.
    should_use_worker: bool  # True if should run in background worker


class MiningProvider(ABC):
    """Abstract base for mining algorithm providers.

    Providers wrap specific mining implementations (PM4Py, ProM, etc.)
    and standardize their interface for the platform.

    Design goals:
    - Algorithm abstraction: Swap implementations without API changes
    - Validation first: Fail fast before expensive operations
    - Resource estimation: Predict memory/time for capacity planning
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider identifier (e.g., 'pm4py', 'prom', 'celonis')."""

    @property
    @abstractmethod
    def version(self) -> str:
        """Provider version string."""

    @abstractmethod
    def supported_miners(self) -> list[MinerType]:
        """Return list of supported mining algorithms."""

    @abstractmethod
    def supports_format(self) -> list[ModelFormat]:
        """Return list of supported output formats."""

    @abstractmethod
    def mine(
        self,
        pm4py_log: Any,
        miner_type: MinerType,
        **params: Any,
    ) -> tuple[Any, ModelFormat]:
        """Execute mining algorithm.

        Args:
            pm4py_log: PM4Py EventLog object
            miner_type: Algorithm to use
            **params: Algorithm-specific parameters

        Returns:
            Tuple of (model_data, format)

        Raises:
            ValueError: If miner_type not supported
            RuntimeError: If mining fails
        """

    @abstractmethod
    def validate_input(self, pm4py_log: Any, miner_type: MinerType) -> list[str]:
        """Validate input before mining.

        Args:
            pm4py_log: PM4Py EventLog object
            miner_type: Algorithm to use

        Returns:
            List of error codes (empty if valid)
        """

    @abstractmethod
    def estimate_complexity(self, pm4py_log: Any, miner_type: MinerType) -> ComplexityEstimate:
        """Estimate resource requirements.

        Args:
            pm4py_log: PM4Py EventLog object
            miner_type: Algorithm to use

        Returns:
            ComplexityEstimate with memory/time predictions
        """
