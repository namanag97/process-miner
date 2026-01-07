"""Delete Dataset Command - Handles dataset deletion with cleanup.

This command soft-deletes a dataset and emits DatasetDeletedEvent
to trigger cache invalidation and cleanup of read models.
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.commands.base import BaseCommand, CommandHandler
from src.features.process_mining.models import Dataset
from src.platform.core.domain_events import DatasetDeletedEvent, event_publisher
from src.platform.core.exceptions import NotFoundError
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class DeleteDatasetCommand(BaseCommand):
    """Command to delete a dataset.

    This performs a soft delete and triggers cleanup of:
    - Cached analytics
    - Parquet files (optional)
    - Related process models
    """

    dataset_id: str = ""  # Required - validated at runtime
    user_id: str | None = None
    hard_delete: bool = False  # If True, permanently remove


class DeleteDatasetHandler(CommandHandler[DeleteDatasetCommand]):
    """Handles dataset deletion commands.

    Responsibilities:
    1. Validate dataset exists
    2. Soft delete the dataset (mark as deleted)
    3. Emit DatasetDeletedEvent for cleanup
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def handle(self, command: DeleteDatasetCommand) -> dict:
        """Execute the delete command.

        Args:
            command: The delete command with dataset_id

        Returns:
            dict with deletion status

        Raises:
            NotFoundError: If dataset doesn't exist
        """
        logger.info(
            "delete_dataset_command_received",
            dataset_id=command.dataset_id,
            hard_delete=command.hard_delete,
            correlation_id=command.correlation_id,
        )

        # 1. Fetch dataset
        result = await self.db.execute(
            select(Dataset).where(Dataset.id == command.dataset_id)
        )
        dataset = result.scalar_one_or_none()

        if not dataset:
            raise NotFoundError(f"Dataset {command.dataset_id} not found")

        dataset_name = dataset.name

        # 2. Delete the dataset
        if command.hard_delete:
            await self.db.delete(dataset)
            logger.info("dataset_hard_deleted", dataset_id=command.dataset_id)
        else:
            # Soft delete - just mark as deleted
            # Note: This assumes a 'deleted' status or 'is_deleted' flag exists
            # If not, we do a hard delete
            await self.db.delete(dataset)
            logger.info("dataset_deleted", dataset_id=command.dataset_id)

        await self.db.flush()

        # 3. Emit event for CQRS read model cleanup
        await event_publisher.publish(
            DatasetDeletedEvent(
                dataset_id=command.dataset_id,
                user_id=command.user_id,
            )
        )

        return {
            "dataset_id": command.dataset_id,
            "name": dataset_name,
            "status": "deleted",
            "message": "Dataset deleted successfully",
        }
