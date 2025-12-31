"""Projects Router.

Endpoints for managing projects (folders for organizing event logs).
"""

import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func

from src.api.dependencies import DBSession
from src.models.orm import EventLog, Project
from src.models.schemas import (
    ProjectCreateRequest,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
    ProcessResponse,
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


def _event_log_to_response(log: EventLog) -> ProcessResponse:
    """Convert EventLog ORM to ProcessResponse."""
    activities = []
    if log.activities_json:
        try:
            activities = json.loads(log.activities_json)
        except json.JSONDecodeError:
            activities = []

    return ProcessResponse(
        id=log.id,
        name=log.name,
        source_format=log.source_format,
        total_events=log.total_events,
        total_cases=log.total_cases,
        total_activities=log.total_activities,
        activities=activities,
        created_at=log.created_at,
        source_file=log.source_file,
    )


# =============================================================================
# CRUD Endpoints
# =============================================================================


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(
    db: DBSession,
    request: ProjectCreateRequest,
) -> ProjectResponse:
    """
    Create a new project.
    """
    project = Project(
        name=request.name,
        description=request.description,
        tags_json=json.dumps(request.tags) if request.tags else None,
        total_files=0,
        total_analyses=0,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return _project_to_response(project)


@router.get("", response_model=ProjectListResponse)
def list_projects(
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by project name"),
) -> ProjectListResponse:
    """
    List all projects with pagination.
    """
    query = db.query(Project)

    # Apply search filter
    if search:
        query = query.filter(Project.name.ilike(f"%{search}%"))

    # Get total count
    total = query.count()

    # Paginate
    projects = (
        query.order_by(Project.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return ProjectListResponse(
        items=[_project_to_response(p) for p in projects],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project(
    db: DBSession,
    project_id: str,
) -> ProjectDetailResponse:
    """
    Get a project by ID with its event logs.
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get event logs for this project
    event_logs = db.query(EventLog).filter(EventLog.project_id == project_id).all()

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
        total_files=len(event_logs),
        total_analyses=project.total_analyses,
        created_at=project.created_at,
        updated_at=project.updated_at,
        event_logs=[_event_log_to_response(log) for log in event_logs],
    )


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    db: DBSession,
    project_id: str,
    request: ProjectUpdateRequest,
) -> ProjectResponse:
    """
    Update a project.
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if request.name is not None:
        project.name = request.name
    if request.description is not None:
        project.description = request.description
    if request.tags is not None:
        project.tags_json = json.dumps(request.tags)

    project.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(project)

    return _project_to_response(project)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    db: DBSession,
    project_id: str,
) -> None:
    """
    Delete a project.

    Note: Event logs in this project will have their project_id set to NULL
    (they won't be deleted).
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Unlink event logs (they remain, just not in a project)
    db.query(EventLog).filter(EventLog.project_id == project_id).update(
        {EventLog.project_id: None}
    )

    db.delete(project)
    db.commit()


# =============================================================================
# File Management
# =============================================================================


@router.post("/{project_id}/files/{log_id}", response_model=ProjectDetailResponse)
def add_file_to_project(
    db: DBSession,
    project_id: str,
    log_id: str,
) -> ProjectDetailResponse:
    """
    Add an existing event log to a project.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    event_log = db.query(EventLog).filter(EventLog.id == log_id).first()
    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    event_log.project_id = project_id
    project.total_files = (
        db.query(func.count(EventLog.id))
        .filter(EventLog.project_id == project_id)
        .scalar()
        or 0
    )
    project.updated_at = datetime.utcnow()

    db.commit()

    return get_project(db, project_id)


@router.delete("/{project_id}/files/{log_id}", status_code=204)
def remove_file_from_project(
    db: DBSession,
    project_id: str,
    log_id: str,
) -> None:
    """
    Remove an event log from a project (doesn't delete the log).
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    event_log = db.query(EventLog).filter(EventLog.id == log_id).first()
    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    if event_log.project_id != project_id:
        raise HTTPException(status_code=400, detail="Event log is not in this project")

    event_log.project_id = None
    project.total_files = (
        db.query(func.count(EventLog.id))
        .filter(EventLog.project_id == project_id)
        .scalar()
        or 0
    )
    project.updated_at = datetime.utcnow()

    db.commit()
