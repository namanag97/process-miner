"""Notification Service - Email, Slack, Webhooks."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import httpx

logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    """Notification delivery channels."""

    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class NotificationStatus(str, Enum):
    """Notification delivery status."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class NotificationPriority(str, Enum):
    """Notification priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class NotificationConfig:
    """Configuration for a notification channel."""

    channel: NotificationChannel
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Notification:
    """A notification to be sent."""

    id: UUID
    channel: NotificationChannel
    recipient: str
    subject: str
    body: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    status: NotificationStatus = NotificationStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "channel": self.channel.value,
            "recipient": self.recipient,
            "subject": self.subject,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "error": self.error,
        }


class NotificationService:
    """
    Notification Service.
    Handles email, Slack, webhook, and in-app notifications.
    In local dev mode, logs notifications instead of sending.
    """

    def __init__(self):
        self._notifications: Dict[UUID, Notification] = {}
        self._configs: Dict[NotificationChannel, NotificationConfig] = {}
        self._subscribers: Dict[str, List[NotificationConfig]] = {}

        # Default configs (mock mode)
        self._configs[NotificationChannel.EMAIL] = NotificationConfig(
            channel=NotificationChannel.EMAIL,
            enabled=True,
            settings={
                "smtp_host": "localhost",
                "smtp_port": 1025,  # MailHog default
                "from_address": "noreply@processmining.local",
            },
        )
        self._configs[NotificationChannel.SLACK] = NotificationConfig(
            channel=NotificationChannel.SLACK,
            enabled=True,
            settings={
                "webhook_url": None,  # Set via configure
            },
        )

    def configure_channel(
        self,
        channel: NotificationChannel,
        settings: Dict[str, Any],
        enabled: bool = True,
    ) -> None:
        """Configure a notification channel."""
        self._configs[channel] = NotificationConfig(
            channel=channel,
            enabled=enabled,
            settings=settings,
        )
        logger.info(f"Configured notification channel: {channel}")

    def subscribe(
        self,
        event_type: str,
        channel: NotificationChannel,
        recipient: str,
    ) -> None:
        """Subscribe to notifications for an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        self._subscribers[event_type].append(
            {
                "channel": channel,
                "recipient": recipient,
            }
        )

    async def send(
        self,
        channel: NotificationChannel,
        recipient: str,
        subject: str,
        body: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        metadata: Dict[str, Any] = None,
    ) -> Notification:
        """
        Send a notification.

        Args:
            channel: Delivery channel
            recipient: Recipient address/ID
            subject: Notification subject
            body: Notification body
            priority: Priority level
            metadata: Additional metadata

        Returns:
            Notification with delivery status
        """
        notification = Notification(
            id=uuid4(),
            channel=channel,
            recipient=recipient,
            subject=subject,
            body=body,
            priority=priority,
            metadata=metadata or {},
        )

        self._notifications[notification.id] = notification

        # Check if channel is enabled
        config = self._configs.get(channel)
        if not config or not config.enabled:
            notification.status = NotificationStatus.FAILED
            notification.error = f"Channel {channel} is not configured or disabled"
            return notification

        # Send based on channel
        try:
            if channel == NotificationChannel.EMAIL:
                await self._send_email(notification, config)
            elif channel == NotificationChannel.SLACK:
                await self._send_slack(notification, config)
            elif channel == NotificationChannel.WEBHOOK:
                await self._send_webhook(notification, config)
            elif channel == NotificationChannel.IN_APP:
                await self._send_in_app(notification, config)

            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()

        except Exception as e:
            notification.status = NotificationStatus.FAILED
            notification.error = str(e)
            logger.error(f"Failed to send notification: {e}")

        return notification

    async def notify_event(
        self,
        event_type: str,
        subject: str,
        body: str,
        metadata: Dict[str, Any] = None,
    ) -> List[Notification]:
        """Send notifications to all subscribers of an event type."""
        subscribers = self._subscribers.get(event_type, [])
        notifications = []

        for sub in subscribers:
            notification = await self.send(
                channel=sub["channel"],
                recipient=sub["recipient"],
                subject=subject,
                body=body,
                metadata=metadata,
            )
            notifications.append(notification)

        return notifications

    async def _send_email(self, notification: Notification, config: NotificationConfig) -> None:
        """Send email notification (mock - logs to console)."""
        logger.info(f"📧 EMAIL to {notification.recipient}")
        logger.info(f"   Subject: {notification.subject}")
        logger.info(f"   Body: {notification.body[:100]}...")

        # In production, would use aiosmtplib or similar
        # For now, just log the email

    async def _send_slack(self, notification: Notification, config: NotificationConfig) -> None:
        """Send Slack notification."""
        webhook_url = config.settings.get("webhook_url")

        if not webhook_url:
            # Mock mode - just log
            logger.info(f"💬 SLACK to {notification.recipient}")
            logger.info(f"   Message: {notification.subject}")
            logger.info(f"   {notification.body[:100]}...")
            return

        # Real Slack webhook
        payload = {
            "channel": notification.recipient,
            "username": "Process Mining Bot",
            "icon_emoji": ":chart_with_upwards_trend:",
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": notification.subject},
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": notification.body},
                },
            ],
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()

    async def _send_webhook(self, notification: Notification, config: NotificationConfig) -> None:
        """Send webhook notification."""
        webhook_url = notification.metadata.get("webhook_url") or config.settings.get("default_url")

        if not webhook_url:
            logger.info("🔔 WEBHOOK (mock)")
            logger.info(f"   Payload: {notification.subject}")
            return

        payload = {
            "event": notification.subject,
            "data": {
                "body": notification.body,
                "priority": notification.priority.value,
                "timestamp": notification.created_at.isoformat(),
                **notification.metadata,
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

    async def _send_in_app(self, notification: Notification, config: NotificationConfig) -> None:
        """Store in-app notification (for polling by frontend)."""
        # In-app notifications are just stored, frontend polls for them
        logger.info(f"🔔 IN_APP notification stored for {notification.recipient}")

    def get_notification(self, notification_id: UUID) -> Optional[Notification]:
        """Get notification by ID."""
        return self._notifications.get(notification_id)

    def get_notifications(
        self,
        recipient: Optional[str] = None,
        channel: Optional[NotificationChannel] = None,
        status: Optional[NotificationStatus] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get notifications with optional filters."""
        notifications = list(self._notifications.values())

        if recipient:
            notifications = [n for n in notifications if n.recipient == recipient]
        if channel:
            notifications = [n for n in notifications if n.channel == channel]
        if status:
            notifications = [n for n in notifications if n.status == status]

        notifications.sort(key=lambda n: n.created_at, reverse=True)

        return [n.to_dict() for n in notifications[:limit]]

    # Convenience methods for common notifications
    async def notify_log_ingested(
        self, log_id: UUID, log_name: str, case_count: int, event_count: int
    ):
        """Notify that a log was ingested."""
        await self.notify_event(
            "log_ingested",
            f"Event Log Ingested: {log_name}",
            f"Successfully ingested {case_count} cases with {event_count} events.",
            {"log_id": str(log_id), "case_count": case_count, "event_count": event_count},
        )

    async def notify_model_discovered(self, model_id: UUID, model_name: str, miner_type: str):
        """Notify that a model was discovered."""
        await self.notify_event(
            "model_discovered",
            f"Process Model Discovered: {model_name}",
            f"Discovered using {miner_type} miner.",
            {"model_id": str(model_id), "miner_type": miner_type},
        )

    async def notify_conformance_checked(self, fitness: float, is_conformant: bool):
        """Notify conformance check result."""
        status = "✅ Conformant" if is_conformant else "⚠️ Non-conformant"
        await self.notify_event(
            "conformance_checked",
            f"Conformance Check: {status}",
            f"Fitness score: {fitness:.2%}",
            {"fitness": fitness, "is_conformant": is_conformant},
        )

    async def notify_anomaly_detected(self, case_id: str, anomaly_type: str, severity: str):
        """Notify that an anomaly was detected."""
        await self.notify_event(
            "anomaly_detected",
            f"⚠️ Anomaly Detected: {anomaly_type}",
            f"Case {case_id} flagged with {severity} severity.",
            {"case_id": case_id, "anomaly_type": anomaly_type, "severity": severity},
        )


# Singleton instance
notification_service = NotificationService()
