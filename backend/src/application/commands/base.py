"""Base command infrastructure for CQRS write operations.

Provides:
- BaseCommand: Abstract base for all command data classes
- CommandHandler: Handler interface for processing commands
- CommandBus: Dispatcher that routes commands to handlers
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar
from uuid import uuid4

from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound="BaseCommand")


@dataclass
class BaseCommand(ABC):
    """Base class for all commands (write operations).

    Commands represent the intent to change state. They should:
    - Be immutable (use frozen=True in subclasses if needed)
    - Contain all data needed to execute the operation
    - Have a unique correlation_id for tracing

    Example:
        @dataclass
        class CreateDatasetCommand(BaseCommand):
            name: str
            workspace_id: str
    """

    correlation_id: str = field(default_factory=lambda: str(uuid4()))

    @property
    def command_type(self) -> str:
        """Return the command type name for logging/tracing."""
        return self.__class__.__name__


class CommandHandler(ABC, Generic[T]):
    """Abstract handler for processing commands.

    Each command type has exactly one handler. Handlers should:
    - Validate the command
    - Execute the write operation
    - Emit domain events on success
    - Raise exceptions on failure

    Example:
        class CreateDatasetHandler(CommandHandler[CreateDatasetCommand]):
            async def handle(self, cmd: CreateDatasetCommand) -> Dataset:
                # Validate, create, emit event, return result
    """

    @abstractmethod
    async def handle(self, command: T) -> Any:
        """Execute the command and return the result."""


class CommandBus:
    """Dispatches commands to their registered handlers.

    Provides centralized command routing with:
    - Handler registration
    - Logging and tracing
    - Error handling

    Usage:
        bus = CommandBus()
        bus.register(CreateDatasetCommand, CreateDatasetHandler(db, events))
        result = await bus.dispatch(CreateDatasetCommand(name="..."))
    """

    def __init__(self):
        self._handlers: dict[type[BaseCommand], CommandHandler] = {}

    def register(self, command_type: type[T], handler: CommandHandler[T]) -> None:
        """Register a handler for a command type."""
        if command_type in self._handlers:
            raise ValueError(f"Handler already registered for {command_type.__name__}")
        self._handlers[command_type] = handler
        logger.debug("command_handler_registered", command_type=command_type.__name__)

    def register_handler(
        self, command_type: type[T]
    ):
        """Decorator to register a handler for a command type.

        Usage:
            @command_bus.register_handler(CreateDatasetCommand)
            class CreateDatasetHandler(CommandHandler[CreateDatasetCommand]):
                ...
        """
        def decorator(handler_cls: type[CommandHandler[T]]) -> type[CommandHandler[T]]:
            # Note: Handler must be instantiated separately with dependencies
            return handler_cls
        return decorator

    async def dispatch(self, command: BaseCommand) -> Any:
        """Dispatch a command to its handler.

        Args:
            command: The command to execute

        Returns:
            The result from the handler

        Raises:
            ValueError: If no handler is registered for the command type
            Exception: Any exception raised by the handler
        """
        command_type = type(command)
        handler = self._handlers.get(command_type)

        if not handler:
            raise ValueError(f"No handler registered for {command_type.__name__}")

        logger.info(
            "command_dispatched",
            command_type=command.command_type,
            correlation_id=command.correlation_id,
        )

        try:
            result = await handler.handle(command)
            logger.info(
                "command_completed",
                command_type=command.command_type,
                correlation_id=command.correlation_id,
            )
            return result
        except Exception as e:
            logger.error(
                "command_failed",
                command_type=command.command_type,
                correlation_id=command.correlation_id,
                error=str(e),
            )
            raise

    def has_handler(self, command_type: type[BaseCommand]) -> bool:
        """Check if a handler is registered for a command type."""
        return command_type in self._handlers


# Global command bus instance
command_bus = CommandBus()
