"""CLI commands responsible for managing Zephyr test plans."""

import json

from argparse import Namespace
from dataclasses import asdict
from zfr.commands import CommandBase
from zfr.config import DEFAULT_API_SUFFIX
from zfr.dataobjects.plan import PlanCreate, PlanUpdate
from zfr.managers import PlanManager


class CreatePlanCommand(CommandBase):
    """Create a new test plan.

    _See Also_:
        [CommandBase][zfr.commands.CommandBase],
        [GetPlanCommand][zfr.commands.plan.GetPlanCommand],
        [UpdatePlanCommand][zfr.commands.plan.UpdatePlanCommand],
        [DeletePlanCommand][zfr.commands.plan.DeletePlanCommand]
    """

    def execute(self, args: Namespace) -> None:
        """Create a new folder.

        If the command is succesful, the stringified JSON object that contains
        the test plan configuration will be printed to stdout where it can be
        captured and used as the input of another command/script.

        Args:
            args: User provided CLI arguments.

        Raises:
            AuthorizationError: If the specified user does not have permission
                to create test plans.
            RuntimeError: If Zephyr Scale returns an unexpected error.
        """
        result = ""

        manager = PlanManager(
            args.url,
            DEFAULT_API_SUFFIX,
            args.username,
            args.password
        )

        test_plan = PlanCreate(
            project_key=args.project,
            name=args.name,
            owner=args.owner,
            objective=args.objective,
            status=args.status,
            folder=args.folder,
            labels=args.labels.split(',') if args.labels else [],
            issue_links=args.issues.split(',') if args.issues else [],
            custom_fields=json.loads(args.fields) if args.fields else {},
            test_run_keys=args.cycles.split(',') if args.cycles else [],
            attachments=args.attachments.split(',') if args.attachments else []
        )

        new_plan = manager.create(test_plan)
        if new_plan:
            plan_dict = asdict(new_plan)
            result = json.dumps(plan_dict)

        print(result)


class DeletePlanCommand(CommandBase):
    """Delete an existing test plan.

    _See Also_:
        [CommandBase][zfr.commands.CommandBase],
        [CreatePlanCommand][zfr.commands.plan.CreatePlanCommand],
        [GetPlanCommand][zfr.commands.plan.GetPlanCommand],
        [UpdatePlanCommand][zfr.commands.plan.UpdatePlanCommand]
    """

    def execute(self, args: Namespace) -> None:
        """Execute the command.

        If the command is succesful, the stringified JSON object that contains
        the test plan configuration will be printed to stdout where it can be
        captured and used as the input of another command/script.

        Args:
            args: User provided CLI arguments.

        Raises:
            AuthorizationError: If the specified user does not have permission
                to create test plans.
            RuntimeError: If Zephyr Scale returns an unexpected error.
        """
        result = ""

        manager = PlanManager(
            args.url,
            DEFAULT_API_SUFFIX,
            args.username,
            args.password
        )

        deleted_plan = manager.delete(args.key)
        if deleted_plan:
            plan_dict = asdict(deleted_plan)
            result = json.dumps(plan_dict)

        print(result)


class GetPlanCommand(CommandBase):
    """Retrieve an existing test plan.

    ???+ tip "Attachments"
         By default, this will make a second API call to retrieve the list of
         files attached to the test plan, and include them in the returned
         data.

         If attachments aren't required, specify the ```fields``` argument to
         limit the fields that are returned, and avoid making an additional API
         call.

    _See Also_:
        [CommandBase][zfr.commands.CommandBase],
        [CreatePlanCommand][zfr.commands.plan.CreatePlanCommand],
        [UpdatePlanCommand][zfr.commands.plan.UpdatePlanCommand],
        [DeletePlanCommand][zfr.commands.plan.DeletePlanCommand]
    """

    def execute(self, args: Namespace) -> None:
        """Execute the command.

        If the command is succesful, the stringified JSON object that contains
        the delete test plan configuration will be printed to stdout where it
        can be captured and used as the input of another command/script.

        Args:
            args: User provided CLI arguments.

        Raises:
            AuthorizationError: If the specified user does not have permission
                to create test plans.
            RuntimeError: If Zephyr Scale returns an unexpected error.
        """
        result = ""

        manager = PlanManager(
            args.url,
            DEFAULT_API_SUFFIX,
            args.username,
            args.password
        )

        if args.fields:
            plan = manager.get(args.key, args.fields.split(','))
        else:
            plan = manager.get(args.key)
        
        if plan:
            if args.fields is None or 'attachments' in args.fields:
                plan.attachments = manager.get_attachments(args.key)

            plan_dict = asdict(plan)
            result = json.dumps(plan_dict)

        print(result)


class PlanCommand(CommandBase):
    """Top level command for actions related to Zephyr test plan management.

    This command essentially performs a no-op, as it acts as a wrapper for the
    various sub-commands used to create/update folders.

    _See Also_:
        [CommandBase][zfr.commands.CommandBase],
        [CreatePlanCommand][zfr.commands.plan.CreatePlanCommand],
        [GetPlanCommand][zfr.commands.plan.GetPlanCommand],
        [UpdatePlanCommand][zfr.commands.plan.UpdatePlanCommand],
        [DeletePlanCommand][zfr.commands.plan.DeletePlanCommand]
    """

    def execute(self, args: Namespace) -> None:
        """Execute the command.

        This will simply display help information, as the ```FolderCommand```
        command acts as a wrapper for sub-commands used to create/update
        Zephyr folders.

        Args:
            args: User provided CLI arguments.
        """
        print("execute")
        self._cli.print_help()


class UpdatePlanCommand(CommandBase):
    """Update an existing test plan.

    _See Also_:
        [CommandBase][zfr.commands.CommandBase],
        [CreatePlanCommand][zfr.commands.plan.CreatePlanCommand],
        [GetPlanCommand][zfr.commands.plan.GetPlanCommand],
        [DeletePlanCommand][zfr.commands.plan.DeletePlanCommand]
    """

    def execute(self, args: Namespace) -> None:
        """Execute the command.

        If the command is succesful, the stringified JSON object that contains
        the updated test plan configuration will be printed to stdout where it
        can be captured and used as the input of another command/script.

        Args:
            args: User provided CLI arguments.

        Raises:
            AuthorizationError: If the specified user does not have permission
                to create test plans.
            RuntimeError: If Zephyr Scale returns an unexpected error.
        """
        result = ""

        manager = PlanManager(
            args.url,
            DEFAULT_API_SUFFIX,
            args.username,
            args.password
        )

        test_plan = PlanUpdate(
            key=args.key,
            name=args.name,
            owner=args.owner,
            objective=args.objective,
            status=args.status,
            folder=args.folder,
            labels=args.labels.split(',') if args.labels else [],
            issue_links=args.issues.split(',') if args.issues else [],
            custom_fields=json.loads(args.fields) if args.fields else {},
            test_runs=args.cycles.split(',') if args.cycles else [],
            attachments=args.attachments.split(',') if args.attachments else []
        )

        updated_plan = manager.update(test_plan)
        if updated_plan:
            plan_dict = asdict(updated_plan)
            result = json.dumps(plan_dict)

        print(result)
