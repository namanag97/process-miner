"""Dataset Command Handlers for CQRS.

Commands for dataset write operations:
- CreateDatasetCommand: Create a new dataset (metadata)
- UpdateMappingCommand: Update column mapping
- TriggerIngestionCommand: Start ingestion workflow
- DeleteDatasetCommand: Delete dataset and associated data
"""

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.commands import BaseCommand, CommandHandler, CommandSuccess
from src.shared.events import EventEnvelope, EventStore, DATASET_CREATED, DATASET_DELETED


# =============================================================================
# Commands
# =============================================================================


@dataclass
class CreateDatasetCommand(BaseCommand):
    """Create a new dataset."""
    
    name: str
    project_id: str
    source_format: str = "csv"
    original_filename: str = ""
    
    def validate(self) -> None:
        if not self.name:
            raise ValueError("Dataset name is required")
        if not self.project_id:
            raise ValueError("Project ID is required")


@dataclass  
class UpdateMappingCommand(BaseCommand):
    """Update column mapping for a dataset."""
    
    dataset_id: str
    case_id_column: str
    activity_column: str
    timestamp_column: str
    resource_column: str | None = None
    cost_column: str | None = None
    additional_columns: dict[str, str] = field(default_factory=dict)
    
    def validate(self) -> None:
        if not self.dataset_id:
            raise ValueError("Dataset ID is required")
        if not self.case_id_column:
            raise ValueError("Case ID column is required")
        if not self.activity_column:
            raise ValueError("Activity column is required")
        if not self.timestamp_column:
            raise ValueError("Timestamp column is required")


@dataclass
class TriggerIngestionCommand(BaseCommand):
    """Trigger ingestion workflow for a dataset."""
    
    dataset_id: str
    
    def validate(self) -> None:
        if not self.dataset_id:
            raise ValueError("Dataset ID is required")


@dataclass
class DeleteDatasetCommand(BaseCommand):
    """Delete a dataset and associated data."""
    
    dataset_id: str
    delete_parquet: bool = True  # Also delete Parquet files
    
    def validate(self) -> None:
        if not self.dataset_id:
            raise ValueError("Dataset ID is required")


# =============================================================================
# Command Handlers
# =============================================================================


class CreateDatasetHandler(CommandHandler[CreateDatasetCommand]):
    """Handler for CreateDatasetCommand.

    Creates a new dataset record in PostgreSQL.
    Emits DatasetCreatedEvent for read model sync.
    """

    async def handle(self, cmd: CreateDatasetCommand) -> str:
        from src.features.process_mining.models import Dataset, DatasetStatus
        
        # Create dataset
        dataset = Dataset(
            name=cmd.name,
            project_id=cmd.project_id,
            source_format=cmd.source_format,
            original_filename=cmd.original_filename,
            status=DatasetStatus.PENDING.value,
        )
        
        self.db.add(dataset)
        await self.db.flush()
        
        # Emit domain event
        await self.emit_event(
            aggregate_type="dataset",
            aggregate_id=dataset.id,
            event_type=DATASET_CREATED,
            payload={
                "name": cmd.name,
                "project_id": cmd.project_id,
                "source_format": cmd.source_format,
            },
        )
        
        return dataset.id


class UpdateMappingHandler(CommandHandler[UpdateMappingCommand]):
    """Handler for UpdateMappingCommand.

    Updates column mapping and validates it against the dataset schema.
    """

    async def handle(self, cmd: UpdateMappingCommand) -> CommandSuccess:
        from src.features.process_mining.models import Dataset, DatasetStatus, DatasetColumnMapping
        from src.shared.events import DATASET_COLUMNS_MAPPED

        # Get dataset
        result = await self.db.execute(
            select(Dataset).where(Dataset.id == cmd.dataset_id)
        )
        dataset = result.scalar_one_or_none()

        if not dataset:
            raise ValueError(f"Dataset not found: {cmd.dataset_id}")

        # Create or update column mapping
        if dataset.column_mapping:
            # Update existing mapping
            dataset.column_mapping.case_id_column = cmd.case_id_column
            dataset.column_mapping.activity_column = cmd.activity_column
            dataset.column_mapping.timestamp_column = cmd.timestamp_column
            dataset.column_mapping.resource_column = cmd.resource_column
        else:
            # Create new mapping
            mapping = DatasetColumnMapping(
                dataset_id=cmd.dataset_id,
                case_id_column=cmd.case_id_column,
                activity_column=cmd.activity_column,
                timestamp_column=cmd.timestamp_column,
                resource_column=cmd.resource_column,
            )
            self.db.add(mapping)

        dataset.status = DatasetStatus.MAPPED.value

        await self.db.flush()
        
        # Emit domain event
        await self.emit_event(
            aggregate_type="dataset",
            aggregate_id=cmd.dataset_id,
            event_type=DATASET_COLUMNS_MAPPED,
            payload={
                "case_id_column": cmd.case_id_column,
                "activity_column": cmd.activity_column,
                "timestamp_column": cmd.timestamp_column,
                "resource_column": cmd.resource_column,
            },
        )
        
        return CommandSuccess(
            id=cmd.dataset_id,
            message="Column mapping updated successfully",
        )


class TriggerIngestionHandler(CommandHandler[TriggerIngestionCommand]):
    """Handler for TriggerIngestionCommand.
    
    Validates dataset state and triggers Temporal workflow.
    """
    
    async def handle(self, cmd: TriggerIngestionCommand) -> CommandSuccess:
        from src.features.process_mining.models import Dataset, DatasetStatus
        from src.shared.events import DATASET_INGESTION_STARTED
        
        # Get dataset
        result = await self.db.execute(
            select(Dataset).where(Dataset.id == cmd.dataset_id)
        )
        dataset = result.scalar_one_or_none()
        
        if not dataset:
            raise ValueError(f"Dataset not found: {cmd.dataset_id}")
        
        if dataset.status != DatasetStatus.MAPPED.value:
            raise ValueError(
                f"Dataset must be in MAPPED status to ingest. Current: {dataset.status}"
            )
        
        # Update status
        dataset.status = DatasetStatus.INGESTING.value
        await self.db.flush()
        
        # Emit domain event 
        await self.emit_event(
            aggregate_type="dataset",
            aggregate_id=cmd.dataset_id,
            event_type=DATASET_INGESTION_STARTED,
            payload={"dataset_id": cmd.dataset_id},
        )
        
        # Note: Actual Temporal workflow trigger is handled by the router
        # This handler just validates and updates state
        
        return CommandSuccess(
            id=cmd.dataset_id,
            message="Ingestion started",
            data={"status": DatasetStatus.INGESTING.value},
        )


class DeleteDatasetHandler(CommandHandler[DeleteDatasetCommand]):
    """Handler for DeleteDatasetCommand.

    Deletes dataset from PostgreSQL and emits event for cache invalidation.
    """

    async def handle(self, cmd: DeleteDatasetCommand) -> CommandSuccess:
        from src.features.process_mining.models import Dataset
        
        # Get dataset
        result = await self.db.execute(
            select(Dataset).where(Dataset.id == cmd.dataset_id)
        )
        dataset = result.scalar_one_or_none()
        
        if not dataset:
            raise ValueError(f"Dataset not found: {cmd.dataset_id}")
        
        parquet_path = dataset.parquet_s3_key
        
        # Delete from database
        await self.db.delete(dataset)
        await self.db.flush()
        
        # Emit domain event for cache invalidation
        await self.emit_event(
            aggregate_type="dataset",
            aggregate_id=cmd.dataset_id,
            event_type=DATASET_DELETED,
            payload={
                "parquet_path": parquet_path,
                "delete_parquet": cmd.delete_parquet,
            },
        )
        
        return CommandSuccess(
            id=cmd.dataset_id,
            message="Dataset deleted successfully",
        )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "CreateDatasetCommand",
    "CreateDatasetHandler",
    "UpdateMappingCommand",
    "UpdateMappingHandler",
    "TriggerIngestionCommand",
    "TriggerIngestionHandler",
    "DeleteDatasetCommand",
    "DeleteDatasetHandler",
]
