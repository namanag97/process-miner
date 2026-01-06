"""Entity-Specific Repositories.

Concrete repository implementations extending BaseRepository.
These provide domain-specific query methods beyond basic CRUD.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.features.process_mining.models import (
    Analysis,
    Dataset,
    ProcessModel,
)
from src.platform.dag.models import DAGDefinition, DAGRun
from src.platform.models import AsyncJob, Project
from src.shared.base_repository import BaseRepository


class AnalysisRepository(BaseRepository[Analysis]):
    """Repository for Analysis aggregate."""
    
    model_class = Analysis
    
    async def get_by_dataset(self, dataset_id: str) -> list[Analysis]:
        """Get all analyses for a dataset."""
        stmt = (
            select(Analysis)
            .where(Analysis.dataset_id == dataset_id)
            .order_by(Analysis.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_latest_by_type(
        self,
        dataset_id: str,
        analysis_type: str,
    ) -> Analysis | None:
        """Get latest analysis of a specific type for a dataset."""
        stmt = (
            select(Analysis)
            .where(Analysis.dataset_id == dataset_id)
            .where(Analysis.type == analysis_type)
            .order_by(Analysis.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()


class ProcessModelRepository(BaseRepository[ProcessModel]):
    """Repository for ProcessModel aggregate."""
    
    model_class = ProcessModel
    
    async def get_by_dataset(self, dataset_id: str) -> list[ProcessModel]:
        """Get all process models for a dataset."""
        stmt = (
            select(ProcessModel)
            .where(ProcessModel.source_dataset_id == dataset_id)
            .order_by(ProcessModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_algorithm(
        self,
        dataset_id: str,
        algorithm: str,
    ) -> ProcessModel | None:
        """Get process model by algorithm for a dataset."""
        stmt = (
            select(ProcessModel)
            .where(ProcessModel.source_dataset_id == dataset_id)
            .where(ProcessModel.algorithm == algorithm)
            .order_by(ProcessModel.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()


class DAGDefinitionRepository(BaseRepository[DAGDefinition]):
    """Repository for DAGDefinition aggregate."""
    
    model_class = DAGDefinition
    
    async def get_active(self) -> list[DAGDefinition]:
        """Get all active DAG definitions."""
        stmt = (
            select(DAGDefinition)
            .where(DAGDefinition.is_active == True)
            .order_by(DAGDefinition.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_name(self, name: str) -> DAGDefinition | None:
        """Get DAG definition by name."""
        stmt = (
            select(DAGDefinition)
            .where(DAGDefinition.name == name)
            .where(DAGDefinition.is_active == True)
            .order_by(DAGDefinition.version.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project aggregate."""
    
    model_class = Project
    
    async def get_by_workspace(
        self,
        workspace_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Project], int]:
        """Get projects for a workspace with pagination."""
        return await self.list_all(
            page=page,
            page_size=page_size,
            workspace_id=workspace_id,
        )
    
    async def search_by_name(
        self,
        workspace_id: str,
        query: str,
    ) -> list[Project]:
        """Search projects by name within a workspace."""
        stmt = (
            select(Project)
            .where(Project.workspace_id == workspace_id)
            .where(Project.name.ilike(f"%{query}%"))
            .order_by(Project.name)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


class DatasetRepositoryV2(BaseRepository[Dataset]):
    """Enhanced Dataset repository using BaseRepository."""
    
    model_class = Dataset
    
    async def get_with_metadata(self, dataset_id: str) -> Dataset | None:
        """Get dataset with metadata eagerly loaded."""
        stmt = (
            select(Dataset)
            .options(
                selectinload(Dataset.metadata_record),
                selectinload(Dataset.column_mapping),
            )
            .where(Dataset.id == dataset_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_project(
        self,
        project_id: str,
        status: str | None = None,
    ) -> list[Dataset]:
        """Get datasets for a project, optionally filtered by status."""
        stmt = (
            select(Dataset)
            .where(Dataset.project_id == project_id)
            .order_by(Dataset.created_at.desc())
        )
        if status:
            stmt = stmt.where(Dataset.status == status)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_ready_datasets(self, project_id: str) -> list[Dataset]:
        """Get only ready datasets for a project."""
        return await self.get_by_project(project_id, status="ready")


class JobRepository(BaseRepository[AsyncJob]):
    """Repository for AsyncJob aggregate."""
    
    model_class = AsyncJob
    
    async def get_by_entity(
        self,
        entity_type: str,
        entity_id: str,
    ) -> list[AsyncJob]:
        """Get jobs for an entity."""
        stmt = (
            select(AsyncJob)
            .where(AsyncJob.entity_type == entity_type)
            .where(AsyncJob.entity_id == entity_id)
            .order_by(AsyncJob.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_running_jobs(self, job_type: str | None = None) -> list[AsyncJob]:
        """Get all running jobs, optionally filtered by type."""
        stmt = (
            select(AsyncJob)
            .where(AsyncJob.status.in_(["pending", "running"]))
        )
        if job_type:
            stmt = stmt.where(AsyncJob.job_type == job_type)
        stmt = stmt.order_by(AsyncJob.created_at)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_task_id(self, task_id: str) -> AsyncJob | None:
        """Get job by Celery task ID."""
        stmt = select(AsyncJob).where(AsyncJob.task_id == task_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()


# =============================================================================
# Repository Factory
# =============================================================================


def get_repositories(session: AsyncSession) -> dict:
    """Get all repositories for a session.
    
    Usage:
        repos = get_repositories(session)
        dataset = await repos["dataset"].get_by_id(id)
    """
    return {
        "analysis": AnalysisRepository(session),
        "process_model": ProcessModelRepository(session),
        "dag_definition": DAGDefinitionRepository(session),
        "project": ProjectRepository(session),
        "dataset": DatasetRepositoryV2(session),
        "job": JobRepository(session),
    }
