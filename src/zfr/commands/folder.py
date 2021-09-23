"""CLI commands responsible for managing Zephyr folders.

???+ note "API Limitations"
     Due to limitations in the Zephyr Scale API, the utility is only capable
     of creating new folders, or updating an existing folder.

     It's not currently possible to retrieve or delete an existing folder using
     the official (public) REST API.
"""

import json

from argparse import Namespace
from dataclasses import asdict
from zfr.commands import CommandBase
from zfr.config import DEFAULT_API_SUFFIX
from zfr.dataobjects.folder import Folder, FolderCreate, FolderType
from zfr.managers import FolderManager


class FolderCommand(CommandBase):
    """Top level command for actions related to Zephyr folder management.

    This command essentially performs a no-op, as it acts as a wrapper for the
    various sub-commands used to create/update folders.

    _See Also_:
        [CommandBase][zfr.commands.CommandBase],
        [CreateFolderCommand][zfr.commands.folder.CreateFolderCommand],
        [UpdateFolderCommand][zfr.commands.folder.UpdateFolderCommand]
    """

    def execute(self, args: Namespace) -> None:
        """Execute the command.

        This will simply display help information, as the ```FolderCommand```
        command acts as a wrapper for sub-commands used to create/update
        Zephyr folders.

        Args:
            args: User provided CLI arguments.
        """
        self._cli.print_help()


class CreateFolderCommand(CommandBase):
    """Create a new folder to logically group test plans, cases or cycles.

    _See Also_:
        [CommandBase][zfr.commands.CommandBase],
        [UpdateFolderCommand][zfr.commands.folder.UpdateFolderCommand]
    """

    def execute(self, args: Namespace) -> None:
        """Create a new folder.

        If the command is succesful, the stringified JSON object that contains
        the folder configuration will be printed to stdout where it can be
        captured and used as the input of another command/script.

        Args:
            args: User provided CLI arguments.

        Raises:
            AuthorizationError: If the specified user does not have permission
                to create folders.
            RuntimeError: If Zephyr Scale returns an unexpected error.
        """
        result = ""

        manager = FolderManager(
            args.url,
            DEFAULT_API_SUFFIX,
            args.username,
            args.password
        )

        # The Zephyr Scale UI refers to test runs as "cycles", so to keep
        # things consistent we do a bit of munging here.
        if args.type.lower() == 'cycle':
            folder_type = FolderType('TEST_RUN')
        else:
            folder_type = FolderType(f"TEST_{args.type.upper()}")

        folder = FolderCreate(project_key=args.project, name=args.name, type=folder_type)
        new_folder = manager.create(folder)
        if new_folder:
            folder_dict = asdict(new_folder)
            result = json.dumps(folder_dict)

        print(result)


class UpdateFolderCommand(CommandBase):
    """Update an existing folder.

    _See Also_:
        [CommandBase][zfr.commands.CommandBase],
        [CreateFolderCommand][zfr.commands.folder.CreateFolderCommand]
    """

    def execute(self, args: Namespace) -> None:
        """Update an existing folder.

        If the command is succesful, the stringified JSON object that contains
        the folder configuration will be printed to stdout where it can be
        captured and used as the input of another command/script.

        Args:
            args: User provided CLI arguments.

        Raises:
            AuthorizationError: If the specified user does not have permission
                to create folders.
            RuntimeError: If Zephyr Scale returns an unexpected error.
        """
        result = ""
        manager = FolderManager(
            args.url,
            DEFAULT_API_SUFFIX,
            args.username,
            args.password
        )

        folder = Folder(id=args.id, name=args.name)
        updated_folder = manager.update(folder)
        if updated_folder:
            folder_dict = asdict(updated_folder)
            result = json.dumps(folder_dict)

        print(result)
