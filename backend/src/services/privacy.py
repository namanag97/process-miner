"""Privacy Service - Differential Privacy for Process Mining.

Phase 6 PM4py Integration: Provides privacy-preserving capabilities:
- SaCoFa (Sequence and Attribute Correlation-preserving Frequency Anonymization)
- PRIPEL (Privacy-preserving Event Log publishing)
"""

from typing import Any

import pm4py

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class PrivacyService:
    """
    Privacy Service for anonymizing event logs.

    Uses differential privacy techniques to protect sensitive data
    while preserving process mining utility.
    """

    def anonymize_log(
        self,
        log,
        epsilon: float = 1.0,
        k: int = 10,
        p: int = 20,
    ):
        """
        Anonymize an event log using differential privacy.

        Combines SaCoFa and PRIPEL techniques for comprehensive
        privacy protection.

        Args:
            log: PM4Py event log (EventLog or DataFrame)
            epsilon: Privacy budget (lower = more private, default 1.0)
            k: K-anonymity parameter
            p: PRIPEL percentage parameter

        Returns:
            Anonymized event log
        """
        logger.info(
            "anonymize_log_started",
            epsilon=epsilon,
            k=k,
            p=p,
        )

        try:
            # Apply SaCoFa for sequence preservation
            anonymized = pm4py.anonymize_log(
                log,
                epsilon=epsilon,
                k=k,
                p=p,
            )

            logger.info("anonymize_log_completed")
            return anonymized
        except Exception as e:
            logger.error("anonymize_log_failed", error=str(e))
            raise

    def apply_sacova(
        self,
        log,
        epsilon: float = 1.0,
    ):
        """
        Apply SaCoFa (Sequence and Attribute Correlation-preserving
        Frequency Anonymization) to an event log.

        Preserves sequence patterns while anonymizing frequencies.

        Args:
            log: PM4Py event log
            epsilon: Privacy budget

        Returns:
            Anonymized event log
        """
        try:
            return pm4py.privacy.anonymize_sacova(log, epsilon=epsilon)
        except AttributeError:
            # Fallback to main anonymization
            return self.anonymize_log(log, epsilon=epsilon)

    def apply_pripel(
        self,
        log,
        epsilon: float = 1.0,
        variant: str = "basic",
    ):
        """
        Apply PRIPEL (Privacy-preserving Event Log publishing).

        Generates synthetic event log preserving statistical properties.

        Args:
            log: PM4Py event log
            epsilon: Privacy budget
            variant: PRIPEL variant ("basic" or "advanced")

        Returns:
            Privacy-preserved event log
        """
        try:
            return pm4py.privacy.anonymize_pripel(
                log,
                epsilon=epsilon,
                variant=variant,
            )
        except AttributeError:
            # Fallback to main anonymization
            return self.anonymize_log(log, epsilon=epsilon)

    def get_privacy_metrics(
        self,
        original_log,
        anonymized_log,
    ) -> dict[str, Any]:
        """
        Calculate privacy and utility metrics comparing logs.

        Measures how much privacy protection was achieved and
        how much utility was preserved.

        Args:
            original_log: Original event log
            anonymized_log: Anonymized event log

        Returns:
            Dictionary with privacy and utility metrics
        """
        try:
            # Get basic statistics for comparison
            orig_variants = pm4py.get_variants(original_log)
            anon_variants = pm4py.get_variants(anonymized_log)

            # Calculate utility preservation
            orig_variant_set = set(orig_variants.keys())
            anon_variant_set = set(anon_variants.keys())

            preserved = len(orig_variant_set.intersection(anon_variant_set))
            total_orig = len(orig_variant_set)

            # DFG comparison
            orig_dfg, _, _ = pm4py.discover_dfg(original_log)
            anon_dfg, _, _ = pm4py.discover_dfg(anonymized_log)

            orig_edges = set(orig_dfg.keys())
            anon_edges = set(anon_dfg.keys())

            edge_preserved = len(orig_edges.intersection(anon_edges))

            return {
                "original_variants": total_orig,
                "anonymized_variants": len(anon_variant_set),
                "variant_overlap": preserved,
                "variant_preservation_ratio": preserved / total_orig if total_orig > 0 else 0,
                "original_edges": len(orig_edges),
                "anonymized_edges": len(anon_edges),
                "edge_overlap": edge_preserved,
                "edge_preservation_ratio": edge_preserved / len(orig_edges) if orig_edges else 0,
            }
        except Exception as e:
            return {"error": str(e)}

    def suppress_sensitive_attributes(
        self,
        log,
        attributes: list[str],
    ):
        """
        Suppress (remove) sensitive attributes from log.

        Simple anonymization by removing specified attributes.

        Args:
            log: PM4Py event log (DataFrame)
            attributes: List of attribute names to remove

        Returns:
            Log with attributes removed
        """
        import pandas as pd

        if isinstance(log, pd.DataFrame):
            cols_to_drop = [c for c in attributes if c in log.columns]
            return log.drop(columns=cols_to_drop)
        # For EventLog objects, need to modify in place
        for trace in log:
            for event in trace:
                for attr in attributes:
                    if attr in event:
                        del event[attr]
        return log

    def generalize_timestamps(
        self,
        log,
        precision: str = "day",
    ):
        """
        Generalize timestamps to reduce re-identification risk.

        Args:
            log: PM4Py event log (DataFrame)
            precision: "year", "month", "day", "hour"

        Returns:
            Log with generalized timestamps
        """
        import pandas as pd

        if not isinstance(log, pd.DataFrame):
            # Convert to DataFrame for processing
            log = pm4py.convert_to_dataframe(log)

        timestamp_col = "time:timestamp"
        if timestamp_col in log.columns:
            if precision == "year":
                log[timestamp_col] = (
                    pd.to_datetime(log[timestamp_col]).dt.to_period("Y").dt.to_timestamp()
                )
            elif precision == "month":
                log[timestamp_col] = (
                    pd.to_datetime(log[timestamp_col]).dt.to_period("M").dt.to_timestamp()
                )
            elif precision == "day":
                log[timestamp_col] = pd.to_datetime(log[timestamp_col]).dt.floor("D")
            elif precision == "hour":
                log[timestamp_col] = pd.to_datetime(log[timestamp_col]).dt.floor("H")

        return log


# Singleton instance
privacy_service = PrivacyService()
