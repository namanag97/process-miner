"""CQRS Command Infrastructure.

Commands represent intentions to change state.
CommandHandlers execute commands and emit domain events.

Usage:
    # Define a command
    @dataclass
    class CreateDatasetCommand(BaseCommand):
        name: str
        project_id: str
    
    # Define handler
    class CreateDatasetHandler(CommandHandler[CreateDatasetCommand]):
        async def handle(self, cmd: CreateDatasetCommand) -> str:
            dataset = Dataset(name=cmd.name, project_id=cmd.project_id)
            await self.db.add(dataset)
            await self.event_bus.publish(DatasetCreatedEvent(...))
            return dataset.id
    
    # Execute via bus
    result = await command_bus.execute(CreateDatasetCommand(name="test", project_id="..."))
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.events import EventEnvelope, EventStore

# =============================================================================
# Base Types
# =============================================================================

CommandResult = TypeVar("CommandResult")


@dataclass(kw_only=True)
class BaseCommand:
    """Base class for all commands.
    
    Commands should be immutable value objects that represent
    an intention to change state.
    
    Note: Uses kw_only=True to allow child classes to have required fields.
    All fields must be passed as keyword arguments.
    """
    
    command_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: str | None = None
    correlation_id: str | None = None
    
    def __post_init__(self):
        """Validate command after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Override to add custom validation. Raise ValueError on failure."""
        pass


# =============================================================================
# Command Handler Protocol
# =============================================================================


class CommandHandler(ABC, Generic[CommandResult]):
    """Base class for command handlers.
    
    Handlers are responsible for:
    1. Validating command preconditions
    2. Executing the state change
    3. Emitting domain events for read model sync
    """
    
    def __init__(
        self,
        db: AsyncSession,
        event_store: EventStore | None = None,
    ):
        self.db = db
        self.event_store = event_store
    
    @abstractmethod
    async def handle(self, command: BaseCommand) -> CommandResult:
        """Execute the command and return result."""
        ...
    
    async def emit_event(
        self,
        aggregate_type: str,
        aggregate_id: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        """Emit a domain event after successful command execution."""
        if self.event_store:
            await self.event_store.append(
                EventEnvelope(
                    aggregate_type=aggregate_type,
                    aggregate_id=aggregate_id,
                    event_type=event_type,
                    payload=payload,
                    user_id=getattr(self, "_user_id", None),
                )
            )


# =============================================================================
# Command Bus
# =============================================================================


class CommandBus:
    """Routes commands to their handlers.
    
    The command bus is responsible for:
    1. Finding the appropriate handler for a command
    2. Providing dependencies to the handler
    3. Executing the command within a transaction
    """
    
    def __init__(self, db: AsyncSession, event_store: EventStore | None = None):
        self._db = db
        self._event_store = event_store
        self._handlers: dict[type, type[CommandHandler]] = {}
    
    def register(
        self,
        command_type: type[BaseCommand],
        handler_type: type[CommandHandler],
    ) -> None:
        """Register a handler for a command type."""
        self._handlers[command_type] = handler_type
    
    async def execute(self, command: BaseCommand) -> Any:
        """Execute a command and return the result.
        
        Raises:
            ValueError: If no handler is registered for the command type
            Exception: Any exception raised by the handler
        """
        handler_type = self._handlers.get(type(command))
        if not handler_type:
            raise ValueError(f"No handler registered for {type(command).__name__}")
        
        handler = handler_type(
            db=self._db,
            event_store=self._event_store,
        )
        
        # Set user context if available
        if command.user_id:
            handler._user_id = command.user_id
        
        return await handler.handle(command)


# =============================================================================
# Command Result Types
# =============================================================================


@dataclass
class CommandSuccess:
    """Successful command execution result."""
    
    id: str | None = None
    message: str = "Command executed successfully"
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class CommandFailure:
    """Failed command execution result."""
    
    error: str
    error_code: str = "COMMAND_FAILED"
    details: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "BaseCommand",
    "CommandHandler",
    "CommandBus",
    "CommandSuccess",
    "CommandFailure",
]
