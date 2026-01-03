"""Projects Router.

Endpoints for managing projects (folders for organizing datasets).
"""

import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select

from src.api.dependencies import DBSession
from src.models.orm import Dataset, Project
from src.models.schemas import (
    ProjectCreateRequest,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
    DatasetResponse,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


# =============================================================================
# Helper Functions
# =============================================================================


def _project_to_response(project: Project) -> ProjectResponse:
    """Convert Project ORM to ProjectResponse."""
    tags = []
    if project.tags_json:
        try:
            tags = json.loads(project.tags_json)
        except json.JSONDecodeError:
            tags = []

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        tags=tags,
        total_files=project.total_files,
        total_analyses=project.total_analyses,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _dataset_to_response(dataset: Dataset) -> DatasetResponse:
    """Convert Dataset ORM to DatasetResponse."""
    activities = []
    if dataset.activities_json:
        try:
            activities = json.loads(dataset.activities_json)
        except json.JSONDecodeError:
            activities = []

    return DatasetResponse(
        id=dataset.id,
        name=dataset.name,
        source_format=dataset.source_format,
        total_events=dataset.total_events,
        total_cases=dataset.total_cases,
        total_activities=dataset.total_activities,
        activities=activities,
        created_at=dataset.created_at,
        source_file=dataset.source_file,
        status=dataset.status,  # FIX: Include dataset lifecycle status
    )


# =============================================================================
# CRUD Endpoints
# =============================================================================


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    db: DBSession,
    request: ProjectCreateRequest,
    workspace_id: Optional[str] = Query(None, description="Workspace ID to associate project with"),
) -> ProjectResponse:
    """
    Create a new project, optionally within a workspace.
    """
    project = Project(
        workspace_id=workspace_id,
        name=request.name,
        description=request.description,
        tags_json=json.dumps(request.tags) if request.tags else None,
        total_files=0,
        total_analyses=0,
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    return _project_to_response(project)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by project name"),
    workspace_id: Optional[str] = Query(None, description="Filter by workspace ID"),
) -> ProjectListResponse:
    """
    List all projects with pagination, optionally filtered by workspace.
    """
    # Build base query
    query = select(Project)

    # Apply workspace filter
    if workspace_id:
        query = query.filter(Project.workspace_id == workspace_id)

    # Apply search filter (case-insensitive for all databases)
    if search:
        query = query.filter(func.lower(Project.name).contains(search.lower()))

    # Get total count
    count_query = select(func.count()).select_from(Project)
    if workspace_id:
        count_query = count_query.filter(Project.workspace_id == workspace_id)
    if search:
        count_query = count_query.filter(func.lower(Project.name).contains(search.lower()))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    query = (
        query.order_by(Project.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    projects = result.scalars().all()

    return ProjectListResponse(
        items=[_project_to_response(p) for p in projects],
        total=total,
        page=page,
        page_size=page_size,
        pages=max(1, (total + page_size - 1) // page_size) if total > 0 else 0,
    )


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    db: DBSession,
    project_id: str,
) -> ProjectDetailResponse:
    """
    Get a project by ID with its datasets.
    """
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get datasets for this project
    datasets_result = await db.execute(
        select(Dataset).filter(Dataset.project_id == project_id)
    )
    datasets = datasets_result.scalars().all()

    tags = []
    if project.tags_json:
        try:
            tags = json.loads(project.tags_json)
        except json.JSONDecodeError:
            tags = []

    return ProjectDetailResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        tags=tags,
        total_files=len(datasets),
        total_analyses=project.total_analyses,
        created_at=project.created_at,
        updated_at=project.updated_at,
        datasets=[_dataset_to_response(ds) for ds in datasets],
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    db: DBSession,
    project_id: str,
    request: ProjectUpdateRequest,
) -> ProjectResponse:
    """
    Update a project.
    """
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if request.name is not None:
        project.name = request.name
    if request.description is not None:
        project.description = request.description
    if request.tags is not None:
        project.tags_json = json.dumps(request.tags)

    project.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(project)

    return _project_to_response(project)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    db: DBSession,
    project_id: str,
) -> None:
    """
    Delete a project.

    Note: Event logs in this project will have their project_id set to NULL
    (they won't be deleted).
    """
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Unlink datasets (they remain, just not in a project)
    from sqlalchemy import update
    await db.execute(
        update(Dataset)
        .where(Dataset.project_id == project_id)
        .values(project_id=None)
    )

    await db.delete(project)
    await db.commit()


# =============================================================================
# File Management
# =============================================================================


@router.post("/{project_id}/files/{dataset_id}", response_model=ProjectDetailResponse)
async def add_file_to_project(
    db: DBSession,
    project_id: str,
    dataset_id: str,
) -> ProjectDetailResponse:
    """
    Add an existing dataset to a project.
    """
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    dataset_result = await db.execute(select(Dataset).filter(Dataset.id == dataset_id))
    dataset = dataset_result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    dataset.project_id = project_id

    # Update total_files count
    count_result = await db.execute(
        select(func.count(Dataset.id)).filter(Dataset.project_id == project_id)
    )
    project.total_files = count_result.scalar() or 0
    project.updated_at = datetime.utcnow()

    await db.commit()

    return await get_project(db, project_id)


@router.delete("/{project_id}/files/{dataset_id}", status_code=204)
async def remove_file_from_project(
    db: DBSession,
    project_id: str,
    dataset_id: str,
) -> None:
    """
    Remove a dataset from a project (doesn't delete the dataset).
    """
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    dataset_result = await db.execute(select(Dataset).filter(Dataset.id == dataset_id))
    dataset = dataset_result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if dataset.project_id != project_id:
        raise HTTPException(status_code=400, detail="Dataset is not in this project")

    dataset.project_id = None

    # Update total_files count
    count_result = await db.execute(
        select(func.count(Dataset.id)).filter(Dataset.project_id == project_id)
    )
    project.total_files = count_result.scalar() or 0
    project.updated_at = datetime.utcnow()

    await db.commit()
