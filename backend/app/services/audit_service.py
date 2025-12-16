"""
Audit Service - Centralized logging for all user actions.

Provides a simple interface for logging actions across the application,
with automatic capture of request context.
"""

import json
from datetime import datetime
from typing import Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from ..models import AuditLog, AuditLogCreate, AuditLogFilter
from ..core import get_logger

log = get_logger(__name__)


class AuditService:
    """Service for creating and querying audit logs."""
    
    @staticmethod
    async def log_action(
        db: AsyncSession,
        entity_type: str,
        action: str,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        details: Optional[dict] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """
        Log an action to the audit trail.
        
        Args:
            db: Database session
            entity_type: Type of entity (organization, process, upload, etc.)
            action: Action performed (create, update, delete, view, process)
            entity_id: ID of the affected entity
            user_id: ID of the user performing the action
            details: Additional details as dictionary
            request: FastAPI request for context extraction
        
        Returns:
            Created AuditLog record
        """
        # Extract request context if available
        ip_address = None
        user_agent = None
        request_path = None
        request_method = None
        
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            request_path = str(request.url.path)
            request_method = request.method
        
        # Create audit log
        audit_log = AuditLog(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            details_json=json.dumps(details) if details else None,
            ip_address=ip_address,
            user_agent=user_agent,
            request_path=request_path,
            request_method=request_method,
            created_at=datetime.utcnow(),
        )
        
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
        
        log.info(
            "audit_logged",
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
        )
        
        return audit_log
    
    @staticmethod
    async def get_logs(
        db: AsyncSession,
        filters: AuditLogFilter,
    ) -> list[AuditLog]:
        """
        Query audit logs with filtering.
        
        Args:
            db: Database session
            filters: Filter criteria
            
        Returns:
            List of matching AuditLog records
        """
        from sqlalchemy import select
        
        query = select(AuditLog).order_by(AuditLog.created_at.desc())
        
        if filters.user_id:
            query = query.where(AuditLog.user_id == filters.user_id)
        if filters.entity_type:
            query = query.where(AuditLog.entity_type == filters.entity_type)
        if filters.entity_id:
            query = query.where(AuditLog.entity_id == filters.entity_id)
        if filters.action:
            query = query.where(AuditLog.action == filters.action)
        if filters.start_date:
            query = query.where(AuditLog.created_at >= filters.start_date)
        if filters.end_date:
            query = query.where(AuditLog.created_at <= filters.end_date)
        
        query = query.offset(filters.offset).limit(filters.limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_entity_history(
        db: AsyncSession,
        entity_type: str,
        entity_id: str,
        limit: int = 50,
    ) -> list[AuditLog]:
        """
        Get audit history for a specific entity.
        
        Args:
            db: Database session
            entity_type: Type of entity
            entity_id: ID of the entity
            limit: Maximum records to return
            
        Returns:
            List of AuditLog records for the entity
        """
        from sqlalchemy import select
        
        query = (
            select(AuditLog)
            .where(AuditLog.entity_type == entity_type)
            .where(AuditLog.entity_id == entity_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        
        result = await db.execute(query)
        return list(result.scalars().all())


# Singleton instance
audit_service = AuditService()
