"""Pickle Migration Service.

Migrates legacy pickle-serialized process models to standard formats:
- PNML (ISO/IEC 15909-2) for archival storage
- Graph JSON for frontend visualization

This service preserves the original pickle data during migration for safety.
"""

import json
import pickle
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog

from src.services.serializers import GraphStructureSerializer, PnmlExporter

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.models.orm import ProcessModel

logger = structlog.get_logger(__name__)


@dataclass
class MigrationResult:
    """Result of migrating a single model."""

    model_id: str
    success: bool
    pnml_path: str | None = None
    graph_json: dict[str, Any] | None = None
    error: str | None = None
    duration_ms: float = 0.0


@dataclass
class MigrationReport:
    """Report summarizing a batch migration."""

    total_models: int = 0
    migrated: int = 0
    skipped: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)
    results: list[MigrationResult] = field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate as a percentage."""
        if self.total_models == 0:
            return 100.0
        return (self.migrated / self.total_models) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary for JSON serialization."""
        return {
            "total_models": self.total_models,
            "migrated": self.migrated,
            "skipped": self.skipped,
            "failed": self.failed,
            "success_rate": round(self.success_rate, 2),
            "errors": self.errors[:10],  # Limit to first 10 errors
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class PickleMigrationService:
    """Migrate pickle blobs to standard formats.

    This service handles the migration of legacy pickle-serialized PM4Py models
    to standard, portable formats. It:
    1. Loads the pickle blob from ProcessModel.serialized_model
    2. Exports to PNML and saves to filesystem
    3. Generates graph JSON for frontend visualization
    4. Updates the database with new column values
    5. Preserves original pickle data (for rollback safety)
    """

    def __init__(
        self,
        storage_path: str = "data/models",
        pnml_exporter: PnmlExporter | None = None,
        graph_serializer: GraphStructureSerializer | None = None,
    ) -> None:
        """Initialize the migration service.

        Args:
            storage_path: Base path for storing PNML files
            pnml_exporter: Optional custom PNML exporter
            graph_serializer: Optional custom graph serializer
        """
        self.storage_path = Path(storage_path)
        self.pnml_exporter = pnml_exporter or PnmlExporter()
        self.graph_serializer = graph_serializer or GraphStructureSerializer()

    async def migrate_all_models(
        self,
        session: "AsyncSession",
        batch_size: int = 100,
        dry_run: bool = False,
    ) -> MigrationReport:
        """Process all ProcessModel records with pickle data.

        Args:
            session: Database session
            batch_size: Number of models to process per batch
            dry_run: If True, don't actually save changes

        Returns:
            MigrationReport with summary of results
        """
        from sqlalchemy import select

        from src.models.orm import ProcessModel

        report = MigrationReport(started_at=datetime.utcnow())

        try:
            # Query models that have pickle data but no standard_content_path
            stmt = select(ProcessModel).where(
                ProcessModel.serialized_model.isnot(None),
                ProcessModel.standard_content_path.is_(None),
            ).limit(batch_size)

            result = await session.execute(stmt)
            models = result.scalars().all()

            report.total_models = len(models)

            logger.info(
                "migration_batch_started",
                total_models=report.total_models,
                batch_size=batch_size,
                dry_run=dry_run,
            )

            for model in models:
                migration_result = await self.migrate_single_model(
                    session, model, dry_run=dry_run
                )
                report.results.append(migration_result)

                if migration_result.success:
                    report.migrated += 1
                elif migration_result.error and "already migrated" in migration_result.error.lower():
                    report.skipped += 1
                else:
                    report.failed += 1
                    if migration_result.error:
                        report.errors.append(
                            f"Model {model.id}: {migration_result.error}"
                        )

            if not dry_run:
                await session.commit()

        except Exception as e:
            logger.error("migration_batch_failed", error=str(e))
            report.errors.append(f"Batch migration failed: {e!s}")
            await session.rollback()

        report.completed_at = datetime.utcnow()

        logger.info(
            "migration_batch_completed",
            migrated=report.migrated,
            skipped=report.skipped,
            failed=report.failed,
            success_rate=report.success_rate,
        )

        return report

    async def migrate_single_model(
        self,
        session: "AsyncSession",
        model: "ProcessModel",
        dry_run: bool = False,
    ) -> MigrationResult:
        """Migrate one model, preserving the original pickle data.

        Steps:
        1. Load pickle blob
        2. Export to PNML and save to S3/filesystem
        3. Compute graph JSON
        4. Update database columns
        5. (Do NOT delete pickle - preserve for rollback)

        Args:
            session: Database session
            model: ProcessModel to migrate
            dry_run: If True, don't actually save changes

        Returns:
            MigrationResult with success/failure details
        """
        import time

        start_time = time.time()
        result = MigrationResult(model_id=model.id, success=False)

        try:
            # Skip if already migrated
            if model.standard_content_path is not None:
                result.success = True
                result.error = "Already migrated"
                result.pnml_path = model.standard_content_path
                logger.debug("model_already_migrated", model_id=model.id)
                return result

            # Skip if no pickle data
            if model.serialized_model is None:
                result.error = "No pickle data to migrate"
                logger.warning("model_no_pickle_data", model_id=model.id)
                return result

            # Step 1: Load pickle
            model_data = self._load_pickle(model.serialized_model)
            if model_data is None:
                result.error = "Failed to unpickle model data"
                return result

            # Step 2: Determine model type and export appropriately
            model_type = model.model_format.lower() if model.model_format else "unknown"

            if model_type in ("petri_net", "petrinet", "pn"):
                # Export Petri net to PNML
                pnml_result = self._export_petri_net(model_data, model.id)
                if pnml_result:
                    result.pnml_path = pnml_result["path"]
                    result.graph_json = pnml_result.get("graph_json")
            elif model_type in ("dfg", "directly_follows_graph"):
                # DFG: Generate graph JSON only (no PNML)
                result.graph_json = self._serialize_dfg(model_data)
                result.pnml_path = None  # DFGs don't have PNML representation
            else:
                # Unknown model type - try to serialize as-is
                result.graph_json = self._serialize_generic(model_data)
                logger.warning(
                    "unknown_model_type",
                    model_id=model.id,
                    model_format=model.model_format,
                )

            # Step 3: Save PNML to filesystem (if generated)
            if result.pnml_path and not dry_run:
                pnml_content = pnml_result.get("content")
                if pnml_content:
                    self._save_pnml_file(result.pnml_path, pnml_content)

            # Step 4: Update database columns
            if not dry_run:
                if result.pnml_path:
                    model.standard_content_path = result.pnml_path
                if result.graph_json:
                    model.graph_structure_json = json.dumps(result.graph_json)

                # Add metadata
                metadata = {
                    "migrated_at": datetime.utcnow().isoformat(),
                    "original_format": model.model_format,
                    "miner_type": model.miner_type,
                }
                model.metadata_json = json.dumps(metadata)

            result.success = True
            result.duration_ms = (time.time() - start_time) * 1000

            logger.info(
                "model_migrated_successfully",
                model_id=model.id,
                model_format=model.model_format,
                has_pnml=result.pnml_path is not None,
                has_graph_json=result.graph_json is not None,
                duration_ms=result.duration_ms,
            )

        except Exception as e:
            result.error = str(e)
            result.duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "model_migration_failed",
                model_id=model.id,
                error=str(e),
            )

        return result

    def _load_pickle(self, pickle_data: bytes) -> Any | None:
        """Safely load pickled model data.

        Args:
            pickle_data: Pickled bytes

        Returns:
            Unpickled object or None if failed
        """
        try:
            return pickle.loads(pickle_data)
        except Exception as e:
            logger.error("pickle_load_failed", error=str(e))
            return None

    def _export_petri_net(
        self, model_data: Any, model_id: str
    ) -> dict[str, Any] | None:
        """Export Petri net to PNML and graph JSON.

        Args:
            model_data: Unpickled model data (should contain net, im, fm)
            model_id: Model ID for file naming

        Returns:
            Dict with 'path', 'content', and 'graph_json' keys
        """
        try:
            # Extract net, initial marking, final marking
            if isinstance(model_data, dict):
                net = model_data.get("net") or model_data.get("petri_net")
                im = model_data.get("im") or model_data.get("initial_marking")
                fm = model_data.get("fm") or model_data.get("final_marking")
            elif isinstance(model_data, tuple) and len(model_data) >= 3:
                net, im, fm = model_data[0], model_data[1], model_data[2]
            else:
                logger.warning(
                    "unexpected_model_data_format",
                    model_id=model_id,
                    data_type=type(model_data).__name__,
                )
                return None

            if net is None:
                logger.warning("no_petri_net_found", model_id=model_id)
                return None

            # Generate PNML
            pnml_content = self.pnml_exporter.export(net, im, fm)

            # Generate graph JSON
            graph_json = self.graph_serializer.serialize_petri_net(net, im, fm)

            # Determine file path
            pnml_path = f"models/{model_id}.pnml"

            return {
                "path": pnml_path,
                "content": pnml_content,
                "graph_json": graph_json,
            }

        except Exception as e:
            logger.error(
                "petri_net_export_failed",
                model_id=model_id,
                error=str(e),
            )
            return None

    def _serialize_dfg(self, model_data: Any) -> dict[str, Any] | None:
        """Serialize DFG to graph JSON.

        Args:
            model_data: Unpickled DFG data

        Returns:
            Graph JSON or None if failed
        """
        try:
            if isinstance(model_data, dict):
                dfg = model_data.get("dfg") or model_data.get("graph")
                start_activities = model_data.get("start_activities", {})
                end_activities = model_data.get("end_activities", {})
                activities_count = model_data.get("activities_count")

                if dfg is not None:
                    return self.graph_serializer.serialize_dfg(
                        dfg, start_activities, end_activities, activities_count
                    )

            # If model_data is the DFG itself (dict of (src, tgt) -> count)
            if isinstance(model_data, dict) and all(
                isinstance(k, tuple) and len(k) == 2 for k in model_data
            ):
                return self.graph_serializer.serialize_dfg(
                    model_data, {}, {}
                )

            logger.warning(
                "unexpected_dfg_format",
                data_type=type(model_data).__name__,
            )
            return None

        except Exception as e:
            logger.error("dfg_serialization_failed", error=str(e))
            return None

    def _serialize_generic(self, model_data: Any) -> dict[str, Any] | None:
        """Serialize unknown model type to basic JSON structure.

        Args:
            model_data: Unpickled model data

        Returns:
            Basic metadata JSON or None
        """
        try:
            # Try to extract any useful structure
            if isinstance(model_data, dict):
                return {
                    "type": "generic",
                    "keys": list(model_data.keys())[:20],
                    "metadata": {
                        "original_type": "dict",
                        "key_count": len(model_data),
                    },
                }
            if isinstance(model_data, tuple):
                return {
                    "type": "generic",
                    "metadata": {
                        "original_type": "tuple",
                        "length": len(model_data),
                    },
                }
            return {
                    "type": "generic",
                    "metadata": {
                        "original_type": type(model_data).__name__,
                    },
                }
        except Exception as e:
            logger.error("generic_serialization_failed", error=str(e))
            return None

    def _save_pnml_file(self, relative_path: str, content: str) -> None:
        """Save PNML content to filesystem.

        Args:
            relative_path: Relative path from storage_path
            content: PNML XML content
        """
        full_path = self.storage_path / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.debug("pnml_file_saved", path=str(full_path))


# CLI entry point for manual migration
if __name__ == "__main__":
    import argparse
    import asyncio

    from src.infrastructure.database import async_session_maker

    async def run_migration(batch_size: int, dry_run: bool) -> None:
        """Run migration from CLI."""
        service = PickleMigrationService()

        async with async_session_maker() as session:
            report = await service.migrate_all_models(
                session, batch_size=batch_size, dry_run=dry_run
            )
            logger.info("migration_report", **report.to_dict())

    parser = argparse.ArgumentParser(description="Migrate pickle models to standard formats")
    parser.add_argument("--batch-size", type=int, default=100, help="Models per batch")
    parser.add_argument("--dry-run", action="store_true", help="Don't save changes")

    args = parser.parse_args()
    asyncio.run(run_migration(args.batch_size, args.dry_run))
