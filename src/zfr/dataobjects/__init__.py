"""Data objects used to interact with the Zephyr API."""

import datetime
from dataclasses import dataclass, field


@dataclass
class Comment:
    """Represents a user comment.

    _See Also_:
        [TestPlan][zfr.dataobjects.TestPlan],
        [TestCase][zfr.dataobjects.TestCase],
        [TestCycle][zfr.dataobjects.TestCycle]
    """

    created_by: str = field(default_factory=str)
    """Username of the user that made the comment."""

    created_on: datetime.datetime = None
    """Date and time that the comment create made."""

    body: str = field(default_factory=str)
    """Contents of the comment."""
