"""Integration Service - External System Connectors."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class ConnectorType(str, Enum):
    """Types of external connectors."""

    SAP = "sap"
    SALESFORCE = "salesforce"
    SERVICENOW = "servicenow"
    JIRA = "jira"
    DATABASE = "database"
    REST_API = "rest_api"
    FILE_SYSTEM = "file_system"


class ConnectionStatus(str, Enum):
    """Connector connection status."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class ConnectorConfig:
    """Configuration for an external connector."""

    id: UUID
    name: str
    connector_type: ConnectorType
    settings: Dict[str, Any] = field(default_factory=dict)
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    last_sync: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "connector_type": self.connector_type.value,
            "status": self.status.value,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class SyncResult:
    """Result of a data synchronization."""

    connector_id: UUID
    success: bool
    records_synced: int = 0
    errors: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "connector_id": str(self.connector_id),
            "success": self.success,
            "records_synced": self.records_synced,
            "errors": self.errors,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class BaseConnector(ABC):
    """Base class for external connectors."""

    def __init__(self, config: ConnectorConfig):
        self.config = config

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to external system."""

    @abstractmethod
    async def disconnect(self) -> bool:
        """Close connection to external system."""

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if connection is valid."""

    @abstractmethod
    async def fetch_event_logs(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch event log data from external system."""

    @abstractmethod
    async def get_available_tables(self) -> List[str]:
        """Get list of available tables/objects."""


class MockConnector(BaseConnector):
    """Unified mock connector for development - replaces 4 separate mock classes."""

    # Static mock data keyed by connector type
    MOCK_EVENT_DATA = {
        ConnectorType.SAP: [
            {"case_id": "PO-001", "activity": "Create Purchase Order", "timestamp": "2024-01-01T09:00:00", "resource": "SAP_USER1"},
            {"case_id": "PO-001", "activity": "Approve Purchase Order", "timestamp": "2024-01-01T10:00:00", "resource": "SAP_USER2"},
            {"case_id": "PO-001", "activity": "Send to Vendor", "timestamp": "2024-01-01T11:00:00", "resource": "SAP_USER1"},
            {"case_id": "PO-002", "activity": "Create Purchase Order", "timestamp": "2024-01-02T09:00:00", "resource": "SAP_USER3"},
        ],
        ConnectorType.SALESFORCE: [
            {"case_id": "OPP-001", "activity": "Lead Created", "timestamp": "2024-01-01T09:00:00", "resource": "Sales Rep"},
            {"case_id": "OPP-001", "activity": "Qualified", "timestamp": "2024-01-02T10:00:00", "resource": "Sales Rep"},
            {"case_id": "OPP-001", "activity": "Proposal Sent", "timestamp": "2024-01-05T11:00:00", "resource": "Sales Rep"},
        ],
        ConnectorType.JIRA: [
            {"case_id": "PROJ-1", "activity": "Created", "timestamp": "2024-01-01T09:00:00", "resource": "Developer"},
            {"case_id": "PROJ-1", "activity": "In Progress", "timestamp": "2024-01-02T10:00:00", "resource": "Developer"},
            {"case_id": "PROJ-1", "activity": "Code Review", "timestamp": "2024-01-03T11:00:00", "resource": "Reviewer"},
            {"case_id": "PROJ-1", "activity": "Done", "timestamp": "2024-01-04T12:00:00", "resource": "Developer"},
        ],
        ConnectorType.DATABASE: [
            {"case_id": "CASE-001", "activity": "Start", "timestamp": "2024-01-01T09:00:00"},
            {"case_id": "CASE-001", "activity": "Process", "timestamp": "2024-01-01T10:00:00"},
            {"case_id": "CASE-001", "activity": "End", "timestamp": "2024-01-01T11:00:00"},
        ],
    }

    MOCK_TABLES = {
        ConnectorType.SAP: ["VBAK", "VBAP", "EKKO", "EKPO", "BKPF", "BSEG"],
        ConnectorType.SALESFORCE: ["Opportunity", "Lead", "Contact", "Account", "Case", "Task"],
        ConnectorType.JIRA: ["issues", "projects", "sprints", "boards"],
        ConnectorType.DATABASE: ["events", "cases", "activities", "resources"],
    }

    CONNECTOR_ICONS = {
        ConnectorType.SAP: "🏢",
        ConnectorType.SALESFORCE: "☁️",
        ConnectorType.JIRA: "📋",
        ConnectorType.DATABASE: "🗄️",
    }

    async def connect(self) -> bool:
        icon = self.CONNECTOR_ICONS.get(self.config.connector_type, "🔌")
        host_key = "instance" if self.config.connector_type == ConnectorType.SALESFORCE else "host"
        if self.config.connector_type == ConnectorType.JIRA:
            host_key = "url"
        host = self.config.settings.get(host_key, "mock")
        logger.info(f"{icon} Connecting to {self.config.connector_type.value}: {host}")
        self.config.status = ConnectionStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        self.config.status = ConnectionStatus.DISCONNECTED
        return True

    async def test_connection(self) -> bool:
        return self.config.status == ConnectionStatus.CONNECTED

    async def fetch_event_logs(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return mock event data based on connector type."""
        data = self.MOCK_EVENT_DATA.get(self.config.connector_type, [])
        # For JIRA, substitute project name in case_id
        if self.config.connector_type == ConnectorType.JIRA:
            project = query.get("project", "PROJ")
            data = [{**e, "case_id": f"{project}-1"} for e in data]
        return data

    async def get_available_tables(self) -> List[str]:
        return self.MOCK_TABLES.get(self.config.connector_type, [])


# Legacy aliases for backward compatibility (can be removed once all usages are updated)
MockSAPConnector = MockConnector
MockSalesforceConnector = MockConnector
MockJiraConnector = MockConnector
MockDatabaseConnector = MockConnector


class IntegrationService:
    """
    Integration Service.
    Manages connections to external systems and data synchronization.
    """

    def __init__(self):
        self._connectors: Dict[UUID, ConnectorConfig] = {}
        self._connector_instances: Dict[UUID, BaseConnector] = {}
        self._sync_history: List[SyncResult] = []

    def get_available_connector_types(self) -> List[Dict[str, Any]]:
        """Get list of available connector types."""
        return [
            {
                "type": ConnectorType.SAP.value,
                "name": "SAP ERP",
                "description": "Connect to SAP S/4HANA or ECC",
                "config_fields": ["host", "client", "user", "password"],
            },
            {
                "type": ConnectorType.SALESFORCE.value,
                "name": "Salesforce",
                "description": "Connect to Salesforce CRM",
                "config_fields": ["instance", "username", "password", "security_token"],
            },
            {
                "type": ConnectorType.SERVICENOW.value,
                "name": "ServiceNow",
                "description": "Connect to ServiceNow ITSM",
                "config_fields": ["instance", "username", "password"],
            },
            {
                "type": ConnectorType.JIRA.value,
                "name": "JIRA",
                "description": "Connect to Atlassian JIRA",
                "config_fields": ["url", "email", "api_token"],
            },
            {
                "type": ConnectorType.DATABASE.value,
                "name": "Database",
                "description": "Connect to SQL databases",
                "config_fields": ["db_type", "host", "port", "database", "user", "password"],
            },
            {
                "type": ConnectorType.REST_API.value,
                "name": "REST API",
                "description": "Connect to any REST API",
                "config_fields": ["base_url", "auth_type", "api_key"],
            },
        ]

    def create_connector(
        self,
        name: str,
        connector_type: ConnectorType,
        settings: Dict[str, Any],
    ) -> ConnectorConfig:
        """Create a new connector configuration."""
        config = ConnectorConfig(
            id=uuid4(),
            name=name,
            connector_type=connector_type,
            settings=settings,
        )

        self._connectors[config.id] = config

        # Create connector instance
        self._connector_instances[config.id] = self._create_connector_instance(config)

        logger.info(f"Created connector: {name} ({connector_type})")
        return config

    def _create_connector_instance(self, config: ConnectorConfig) -> BaseConnector:
        """Create connector instance based on type."""
        connectors = {
            ConnectorType.SAP: MockSAPConnector,
            ConnectorType.SALESFORCE: MockSalesforceConnector,
            ConnectorType.JIRA: MockJiraConnector,
            ConnectorType.DATABASE: MockDatabaseConnector,
        }

        connector_class = connectors.get(config.connector_type, MockDatabaseConnector)
        return connector_class(config)

    def get_connector(self, connector_id: UUID) -> Optional[ConnectorConfig]:
        """Get connector by ID."""
        return self._connectors.get(connector_id)

    def list_connectors(self) -> List[Dict[str, Any]]:
        """List all configured connectors."""
        return [c.to_dict() for c in self._connectors.values()]

    def delete_connector(self, connector_id: UUID) -> bool:
        """Delete a connector."""
        if connector_id in self._connectors:
            del self._connectors[connector_id]
            if connector_id in self._connector_instances:
                del self._connector_instances[connector_id]
            return True
        return False

    async def connect(self, connector_id: UUID) -> bool:
        """Connect to external system."""
        instance = self._connector_instances.get(connector_id)
        if not instance:
            return False
        return await instance.connect()

    async def disconnect(self, connector_id: UUID) -> bool:
        """Disconnect from external system."""
        instance = self._connector_instances.get(connector_id)
        if not instance:
            return False
        return await instance.disconnect()

    async def test_connection(self, connector_id: UUID) -> Dict[str, Any]:
        """Test a connector's connection."""
        instance = self._connector_instances.get(connector_id)
        if not instance:
            return {"success": False, "error": "Connector not found"}

        try:
            await instance.connect()
            success = await instance.test_connection()
            return {
                "success": success,
                "status": instance.config.status.value,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def sync_data(
        self,
        connector_id: UUID,
        query: Dict[str, Any] = None,
    ) -> SyncResult:
        """Synchronize data from external system."""
        result = SyncResult(connector_id=connector_id, success=False)

        instance = self._connector_instances.get(connector_id)
        if not instance:
            result.errors.append("Connector not found")
            return result

        try:
            # Connect if not connected
            if instance.config.status != ConnectionStatus.CONNECTED:
                await instance.connect()

            # Fetch data
            data = await instance.fetch_event_logs(query or {})

            result.success = True
            result.records_synced = len(data)

            # Update last sync time
            instance.config.last_sync = datetime.utcnow()

        except Exception as e:
            result.errors.append(str(e))
            logger.error(f"Sync failed: {e}")

        result.completed_at = datetime.utcnow()
        self._sync_history.append(result)

        return result

    async def fetch_event_data(
        self,
        connector_id: UUID,
        query: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch event log data from connector."""
        instance = self._connector_instances.get(connector_id)
        if not instance:
            raise ValueError("Connector not found")

        if instance.config.status != ConnectionStatus.CONNECTED:
            await instance.connect()

        return await instance.fetch_event_logs(query or {})

    async def get_available_tables(self, connector_id: UUID) -> List[str]:
        """Get available tables/objects from connector."""
        instance = self._connector_instances.get(connector_id)
        if not instance:
            raise ValueError("Connector not found")

        if instance.config.status != ConnectionStatus.CONNECTED:
            await instance.connect()

        return await instance.get_available_tables()

    def get_sync_history(
        self,
        connector_id: Optional[UUID] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get synchronization history."""
        history = self._sync_history

        if connector_id:
            history = [r for r in history if r.connector_id == connector_id]

        return [r.to_dict() for r in history[-limit:]]


# Singleton instance
integration_service = IntegrationService()
