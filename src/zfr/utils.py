"""zfr CLI utility methods/objects."""

import os
import re

from argparse import Action
from requests import Response
from requests.adapters import HTTPAdapter
from typing import Dict, List, Union


def camel_to_snake(s: str) -> str:
    """Convert a string from camelCase string to snake_case.

    Args:
        s: String to be converted.

    Returns:
        A string where camelCase words have been converted to snake_case.
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()


def snake_to_camel(s: str) -> str:
    """Convert a string from snake_case to camelCase.

    Args:
        s: String to be converted.

    Returns:
        A string where snake_case words have been converted to camelCase.
    """
    components = s.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def dict_to_snake(data: Union[Dict, List]) -> Dict:
    """Convert dictionary keys from camel case to snake case.

    This function is used when translating dataclasses to/from
    their JSON respresentation in order to align the attribute
    names to what the Zephyr Scale REST API expects to see.

    Args:
        s: String to be converted.

    Returns:
        A dict, where each key has been converted from camelCase to snake_case.
    """
    if isinstance(data, list):
        return [
            dict_to_snake(entry) if isinstance(entry, (dict, list))
            else entry for entry in data
        ]
    else:
        return {
            camel_to_snake(key): dict_to_snake(val) if isinstance(val, (dict, list))
            else val for key, val in data.items()
        }


def dict_to_camel(data: Union[Dict, List]) -> Dict:
    """Convert dictionary keys from snake case to camel case.

    This function is used when translating dataclasses to/from
    their JSON representation in order to align the attribute
    names to what the Zephyr Scale REST API expects to see.

    Args:
        data: The dictionary to convert.

    Returns:
        A new dictionary, where the keys have been translated from snake_case to camelCase.
    """
    if isinstance(data, list):
        return [
            dict_to_camel(entry) if isinstance(entry, (dict, list))
            else entry for entry in data
        ]

    return {
        snake_to_camel(key): dict_to_camel(val) if isinstance(val, (dict, list))
        else val for key, val in data.items()
    }


class EnvDefault(Action):
    """Custom action used to set CLI arguments via environment variables."""

    def __init__(self, envvar: str, required=True, default=None, **kwargs) -> None:
        """Initialize the action.

        Args:
            envvar: Name of the environment variable to read the argument value from.
            required: ```True``` to make the argument mandatory, otherwise ```False```.
            default: Default value is none is specified by the user.
            kwargs: Extra argument configuration options.
        """
        if not default and envvar:
            default = os.getenv(envvar, None)

        if required and default:
            required = False
       
        super(EnvDefault, self).__init__(
            default=default,
            required=required,
            **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class TimeoutHTTPAdapter(HTTPAdapter):
    """Requests adapter used to manage request timeouts."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize a new HTTP adapter with a preset timeout.

        Args:
            args: Standard HTTP Adapter arguments.
            kwargs: Additional arguments.
        """
        self.timeout = 90
        if 'timeout' in kwargs:
            self.timeout = kwargs['timeout']
            del kwargs['timeout']
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs) -> Response:
        """Send the HTTP request.

        Args:
            request:
            kwargs:

        Returns:
            Returns the HTTP response from the remote server.
        """
        timeout = kwargs.get('timeout')
        if timeout is None:
            kwargs['timeout'] = self.timeout
        return super().send(request, **kwargs)
