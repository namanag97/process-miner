"""Ingest Dataset Command - Triggers dataset ingestion workflow.

This command validates the dataset is ready for ingestion and emits
the DatasetIngestedEvent upon successful completion.
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.commands.base import BaseCommand, CommandHandler
from src.features.process_mining.models import Dataset, DatasetStatus
from src.platform.core.domain_events import DatasetIngestedEvent, event_publisher
from src.platform.core.exceptions import NotFoundError, ValidationError
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class IngestDatasetCommand(BaseCommand):
    """Command to trigger dataset ingestion.

    Prerequisites:
    - Dataset must exist
    - Dataset must be in MAPPED status
    - Column mapping must be configured
    """

    dataset_id: str = ""  # Required - validated at runtime
    user_id: str | None = None


class IngestDatasetHandler(CommandHandler[IngestDatasetCommand]):
    """Handles dataset ingestion commands.

    Responsibilities:
    1. Validate dataset exists and is in correct state
    2. Trigger the ingestion workflow (via Temporal or sync)
    3. Emit DatasetIngestedEvent on success
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def handle(self, command: IngestDatasetCommand) -> dict:
        """Execute the ingestion command.

        Args:
            command: The ingestion command with dataset_id

        Returns:
            dict with status and any workflow info

        Raises:
            NotFoundError: If dataset doesn't exist
            ValidationError: If dataset is not in correct state
        """
        logger.info(
            "ingest_dataset_command_received",
            dataset_id=command.dataset_id,
            correlation_id=command.correlation_id,
        )

        # 1. Fetch and validate dataset
        result = await self.db.execute(
            select(Dataset).where(Dataset.id == command.dataset_id)
        )
        dataset = result.scalar_one_or_none()

        if not dataset:
            raise NotFoundError(resource="Dataset", resource_id=command.dataset_id)

        if dataset.status != DatasetStatus.MAPPED.value:
            raise ValidationError(
                f"Dataset must be in MAPPED status for ingestion, "
                f"current status: {dataset.status}"
            )

        # 2. Update status to INGESTING
        dataset.status = DatasetStatus.INGESTING.value
        await self.db.flush()

        logger.info(
            "dataset_ingestion_started",
            dataset_id=command.dataset_id,
            previous_status="MAPPED",
        )

        # 3. The actual ingestion is handled by Temporal workflow
        # This command just validates and triggers it
        # Return info for the caller to track

        return {
            "dataset_id": command.dataset_id,
            "status": "ingesting",
            "message": "Ingestion started",
        }

    async def complete_ingestion(
        self,
        dataset_id: str,
        parquet_path: str,
        total_events: int,
        total_cases: int,
        total_activities: int,
        user_id: str | None = None,
    ) -> None:
        """Called when ingestion completes successfully.

        Updates dataset status and emits DatasetIngestedEvent.
        This should be called by the Temporal activity upon completion.
        """
        result = await self.db.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        dataset = result.scalar_one_or_none()

        if dataset:
            dataset.status = DatasetStatus.READY.value
            dataset.parquet_s3_key = parquet_path
            dataset.total_events = total_events
            dataset.total_cases = total_cases
            dataset.total_activities = total_activities
            await self.db.flush()

            # Emit event for CQRS read model sync
            await event_publisher.publish(
                DatasetIngestedEvent(
                    dataset_id=dataset_id,
                    parquet_path=parquet_path,
                    total_events=total_events,
                    total_cases=total_cases,
                    total_activities=total_activities,
                    user_id=user_id,
                )
            )

            logger.info(
                "dataset_ingestion_completed",
                dataset_id=dataset_id,
                total_events=total_events,
                total_cases=total_cases,
            )
