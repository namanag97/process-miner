"""CQRS Commands - Write Operations.

Commands represent intent to mutate state. Each command has:
- A data class defining the command parameters
- A handler that executes the command
- Optional events emitted on success

Usage:
    command = IngestDatasetCommand(dataset_id="...", file_path="...")
    await command_bus.dispatch(command)
"""

from src.application.commands.base import BaseCommand, CommandBus, CommandHandler, CommandSuccess

__all__ = ["BaseCommand", "CommandBus", "CommandHandler", "CommandSuccess"]
