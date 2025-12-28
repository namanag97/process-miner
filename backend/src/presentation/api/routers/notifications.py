"""Notifications API Router."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID

from src.application.generic.notification_service import (
    notification_service,
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
)
from src.presentation.api.routers.auth import require_auth, User


router = APIRouter(prefix="/notifications")


class SendNotificationRequest(BaseModel):
    channel: str
    recipient: str
    subject: str
    body: str
    priority: str = "medium"
    metadata: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    id: str
    channel: str
    recipient: str
    subject: str
    priority: str
    status: str
    created_at: str
    sent_at: Optional[str]
    error: Optional[str]


class SubscribeRequest(BaseModel):
    event_type: str
    channel: str
    recipient: str


class ConfigureChannelRequest(BaseModel):
    channel: str
    settings: Dict[str, Any]
    enabled: bool = True


@router.post("/send", response_model=NotificationResponse)
async def send_notification(
    request: SendNotificationRequest,
    user: User = Depends(require_auth),
):
    """Send a notification."""
    try:
        channel = NotificationChannel(request.channel)
        priority = NotificationPriority(request.priority)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    notification = await notification_service.send(
        channel=channel,
        recipient=request.recipient,
        subject=request.subject,
        body=request.body,
        priority=priority,
        metadata=request.metadata,
    )
    
    return NotificationResponse(**notification.to_dict())


@router.get("/", response_model=List[NotificationResponse])
async def list_notifications(
    recipient: Optional[str] = None,
    channel: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    user: User = Depends(require_auth),
):
    """List notifications with optional filters."""
    channel_enum = None
    status_enum = None
    
    if channel:
        try:
            channel_enum = NotificationChannel(channel)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid channel: {channel}")
    
    if status:
        try:
            status_enum = NotificationStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    notifications = notification_service.get_notifications(
        recipient=recipient,
        channel=channel_enum,
        status=status_enum,
        limit=limit,
    )
    
    return [NotificationResponse(**n) for n in notifications]


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    user: User = Depends(require_auth),
):
    """Get notification by ID."""
    notification = notification_service.get_notification(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationResponse(**notification.to_dict())


@router.post("/subscribe")
async def subscribe_to_events(
    request: SubscribeRequest,
    user: User = Depends(require_auth),
):
    """Subscribe to notifications for an event type."""
    try:
        channel = NotificationChannel(request.channel)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid channel: {request.channel}")
    
    notification_service.subscribe(
        event_type=request.event_type,
        channel=channel,
        recipient=request.recipient,
    )
    
    return {"message": f"Subscribed to {request.event_type}"}


@router.post("/configure")
async def configure_channel(
    request: ConfigureChannelRequest,
    user: User = Depends(require_auth),
):
    """Configure a notification channel."""
    try:
        channel = NotificationChannel(request.channel)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid channel: {request.channel}")
    
    notification_service.configure_channel(
        channel=channel,
        settings=request.settings,
        enabled=request.enabled,
    )
    
    return {"message": f"Channel {request.channel} configured"}


@router.get("/channels")
async def list_channels(user: User = Depends(require_auth)):
    """List available notification channels."""
    return {
        "channels": [
            {"id": "email", "name": "Email", "description": "Email notifications"},
            {"id": "slack", "name": "Slack", "description": "Slack channel notifications"},
            {"id": "webhook", "name": "Webhook", "description": "Custom webhook notifications"},
            {"id": "in_app", "name": "In-App", "description": "In-application notifications"},
        ]
    }
