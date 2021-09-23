"""zfr-folder CLI that allows users to manage Zephyr Scale folders."""

import os
from configparser import ConfigParser

from pathlib import Path

from argparse import ArgumentParser, _SubParsersAction

from zfr.commands.folder import (
    CreateFolderCommand,
    FolderCommand,
    UpdateFolderCommand
)

from zfr.utils import EnvDefault

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
        print("loading")
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
        The main zfr-folder parser.
    """
    parsers = [parser]
    parser = ArgumentParser(description='Manager zephyr scale folders.', parents=parsers)        
    parser.set_defaults(**defaults)
    return parser


def cli() -> None:
    """Generates the zfr-folder CLI utility to manage  folders in Zephyr Scale.

    Returns:
        Returns an ArgumentParser that contains all of the sub-commands used to
        manipulate Zephyr Scale folders.
    """
    config_argparse = _configfile_parser()
    config_args, _ = config_argparse.parse_known_args()

    defaults = {}

    if config_args.config:    
        defaults = _load_config(config_args)

    parser = _cli(config_argparse, defaults)
    _add_standard_args(parser)    
   
    subparser = parser.add_subparsers()
    _add_create_command(subparser)
    _add_update_command(subparser)    

    args = parser.parse_args()
    command = args.cmd
    command.execute(args)


def _add_create_command(subparser: _SubParsersAction):
    """Sub-command used to create new Zephyr folders.

    Args:
        subparser: Parent that the sub-command will belong to.
    """
    parser = subparser.add_parser('create', help='Create a new folder.')    
    parser.add_argument(
        '--project',
        required=True,
        help='Project key of the project that the folder will be created under.'
    )
    parser.add_argument(
        '--name',
        required=False,
        help='Name of the folder.'
    )
    parser.add_argument(
        '--type',
        required=False,
        choices=['plan', 'case', 'cycle'],
        help='Type of folder to create.',
    )
    parser.set_defaults(cmd=CreateFolderCommand(parser))


def _add_standard_args(parser: ArgumentParser) -> None:
    """Standard arguments that are applicable to all zfr-folder sub-commands.

    Args:
        parser: Main parser that provides the zfr-folder utility.
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
    parser.set_defaults(cmd=FolderCommand(parser))


def _add_update_command(subparser: _SubParsersAction) -> None:
    """Sub-command used to update an existing Zephyr folder.

    Args:
        subparser: Parent that the sub-command will belong to.
    """
    parser = subparser.add_parser('update', help='Update an existing folder.')
    parser.add_argument(
        '--id',
        required=True,
        help='Unique id of the folder to be updated.'
    )
    parser.add_argument(
        '--name',
        required=True,
        help='Name to assign to the folder.'
    )
    parser.set_defaults(cmd=UpdateFolderCommand(parser))
