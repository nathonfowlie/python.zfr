"""CLI commands responsible for manipulating Zephyr test plans/cases/cycles."""

from abc import ABC, abstractmethod
from argparse import _SubParsersAction, ArgumentParser, Namespace


class CommandBase(ABC):
    """Base class for CLI commands used to manage Zephyr test configuration."""

    def __init__(self, cli: ArgumentParser) -> None:
        """Initialise the sub-command.

        Args:
            cli: ArgParse action that will execute this command.
        """
        self._cli = cli

    @abstractmethod
    def execute(self, args: Namespace) -> None:
        """Execute the command.

        Args:
            args: User provided CLI arguments.
        """
        pass
