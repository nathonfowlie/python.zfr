"""zfr-plan CLI that allows users to manage Zephyr Scale test plans."""

import os
from argparse import ArgumentParser, _SubParsersAction

from configparser import ConfigParser
from pathlib import Path

from zfr.commands.plan import (
    CreatePlanCommand,
    DeletePlanCommand,
    GetPlanCommand,
    PlanCommand,
    UpdatePlanCommand
)

from zfr.utils import EnvDefault


def cli() -> None:
    """Generates the zfr-plan CLI used to manage test plans in Zephyr Scale.

    Returns:
        Returns an ArgumentParser that contains all of the sub-commands used to
        manipulate Zephyr Scale test plans.
    """
    config_argparse = _configfile_parser()
    config_args, _ = config_argparse.parse_known_args()

    defaults = {}

    if config_args.config:    
        defaults = _load_config(config_args)

    parser = _cli(config_argparse, defaults)
    subparser = parser.add_subparsers()

    _add_standard_args(parser)    
    _add_create_command(subparser)
    _add_get_command(subparser)
    _add_update_command(subparser)
    _add_delete_command(subparser)
   
    args = parser.parse_args()
    command = args.cmd
    command.execute(args)


def _add_create_command(subparser: _SubParsersAction) -> None:
    """Sub-command used to create new Zephyr Scale test plans.

    Args:
        subparser: Parent that the sub-command will belong to.
    """
    parser = subparser.add_parser('create', help='Create a new test plan.')

    parser.add_argument(
        '--project',
        required=True,
        help='Project key of the project that the test plan will be created under.'
    )
    parser.add_argument(
        '--name',
        required=False,
        help='Name of the test plan.'
    )
    parser.add_argument(
        '--objective',
        required=False,
        help='Objectives of the test plan.'
    )
    parser.add_argument(
        '--folder',
        required=False,
        help=('Name of the folder used to logically group test plans. If the '
              'folder does not exist, it will be created.')
    )
    parser.add_argument(
        '--labels',
        required=False,
        help=('Comma seperated list of labels that can be used to further '
              'categorise test plans.')
    )
    parser.add_argument(
        '--issues',
        required=False,
        help=('Comma seperated list of Jira issues that should be linked to '
              'the test plan.')
    )
    parser.add_argument(
        '--cycles',
        required=False,
        help=('Comma seperated list of test cycles that will be associated with '
              'the test plan.')
    )
    parser.add_argument(
        '--fields',
        required=False,
        help='List of additional custom fields, provided as a JSON string.'
    )
    parser.add_argument(
        '--owner',
        required=False,
        help='Username of the person responsible for maintaining the test plan.'
    )
    parser.add_argument(
        '--status',
        required=False,
        choices=['Draft', 'Deprecated', 'Approved'],
        help='Test plan status.'
    )
    parser.add_argument(
        '--attachments',
        required=False,
        help='Comma seperated list of file paths.'
    )
    parser.set_defaults(cmd=CreatePlanCommand(parser))


def _add_delete_command(subparser: _SubParsersAction) -> None:
    """Sub-command used to delete existing Zephyr Scale test plans.

    Args:
        subparser: Parent that the sub-command will belong to.
    """
    parser = subparser.add_parser('delete', help='Delete an existing test plan.')
    parser.add_argument(
        '--key',
        required=True,
        help='Test plan key (eg: MYPROJECT-P34).'
    )
    parser.set_defaults(cmd=DeletePlanCommand(parser))


def _add_get_command(subparser: _SubParsersAction) -> None:
    """Sub-command used to retrieve existing Zephyr Scale test plans.

    Args:
        subparser: Parent that the sub-command will belong to.
    """
    parser = subparser.add_parser('get', help='Get an existing test plan.')
    parser.add_argument(
        '--key',
        required=True,
        help='Test plan key (eg: MYPROJECT-P34).'
    )
    parser.add_argument(
        '--fields',
        required=False,
        help='Limit which fields are returned (comma seperated list).'
    )
    parser.set_defaults(cmd=GetPlanCommand(parser))


def _add_standard_args(parser: ArgumentParser) -> None:
    """Standard arguments that are applicable to all zfr-plan sub-commands.

    Args:
        parser: Main parser that provides the zfr-plan utility.
    """
    parser.add_argument(
        '--username',
        required=True,
        action=EnvDefault,
        envvar='ZFR_USERNAME',
        help='Username used to login to Zephyr Scale.'
    )
    parser.add_argument(
        '--password',
        required=True,
        action=EnvDefault,
        envvar='ZFR_PASSWORD',
        help='Password used to login to Zephyr Scale.'
    )
    parser.add_argument(
        '--url',
        required=True,
        action=EnvDefault,
        envvar='ZFR_URL',
        help='Jira url used to interace with the Zephyr API.'
    )
    parser.set_defaults(cmd=PlanCommand(parser))


def _add_update_command(subparser: _SubParsersAction) -> None:    
    """Sub-command used to update existing Zephyr Scale test plans.

    Args:
        subparser: Parent that the sub-command will belong to.
    """
    parser = subparser.add_parser('update', help='Update an existing test plan.')

    parser.add_argument(
        '--project',
        required=True,
        help='Project key of the project that the test plan will reside under.'
    )
    parser.add_argument(
        '--key',
        required=True,
        help='Test plan key (eg: MYPROJECT-P32).'
    )
    parser.add_argument(
        '--name',
        required=False,
        help='Name of the test plan.'
    )
    parser.add_argument(
        '--objective',
        required=False,
        help='Objectives of the test plan.'
    )
    parser.add_argument(
        '--folder',
        required=False,
        help=('Name of the folder used to logically group test plans. If the '
              'folder does not exist, it will be created.')
    )
    parser.add_argument(
        '--labels',
        required=False,
        help=('Comma seperated list of labels that can be used to further '
              'categorise test plans.')
    )
    parser.add_argument(
        '--issues',
        required=False,
        help=('Comma seperated list of Jira issues that should be linked to '
              'the test plan.')
    )
    parser.add_argument(
        '--cycles',
        required=False,
        help=('Comma seperated list of test cycles that will be associated with '
              'the test plan.')
    )
    parser.add_argument(
        '--fields',
        required=False,
        help='List of additional custom fields, provided as a JSON string.'
    )
    parser.add_argument(
        '--owner',
        required=False,
        help='Username of the person responsible for maintaining the test plan.'
    )
    parser.add_argument(
        '--status',
        required=False,
        choices=['Draft', 'Deprecated', 'Approved'],
        help='Test plan status.'
    )
    parser.add_argument(
        '--attachments',
        required=False,
        help='Comma seperated list of file paths.'
    )
    parser.set_defaults(cmd=UpdatePlanCommand(parser))

def _configfile_parser() -> ArgumentParser:
    """
    
    Returns:
    """
    parser = ArgumentParser(prog=__file__, add_help=False)
    parser.add_argument('--config', default=Path.joinpath(Path.home(), 'zfr.cfg'), help='Path to the configuration file.')
    return parser

def _load_config(args):
    """

    Args:    
    """

    if os.path.isfile(args.config):
        config_parser = ConfigParser()

        with open(args.config) as infile:
            config_parser.read_file(infile)
        config_parser.read(args.config)

        return dict(config_parser.items('jira'))
    else:
        return {}


def _cli(parser, defaults) -> ArgumentParser:
    """Create the main CLI parser.

    Where a configuration file is found, this will load CLI options from the
    file, over-riding any configuration set via environment variables.

    Args:
        parser: Parser used to read the configuration file.
        defaults: Dictionary that contains the CLI argument default values.

    Returns:
        The main zfr-plan parser.
    """
    parsers = [parser]
    parser = ArgumentParser(description='Manager zephyr scale test plans.', parents=parsers)        
    parser.set_defaults(**defaults)
    return parser