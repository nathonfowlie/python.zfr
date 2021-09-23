"""Data objects used to manage test cycles."""

import datetime

from dataclasses import dataclass, field


@dataclass
class TestCycle:
    """Represents an existing test cycle.

    _See Also_:
        [TestPlan][zfr.dataobjects.TestPlan]
    """

    created_by: str = field(default_factory=str)
    """Username of the user that created the test cycle."""

    created_on: datetime.datetime = None
    """Date and time that the test cycle was created."""

    description: str = field(default_factory=str)
    """Brief description of the purpose of the test cycle."""

    estimated_time: int = field(default_factory=int)
    """Estimated time (in seconds) required to complete the test cycle."""

    folder: str = field(default_factory=str)
    """Folder used to logically group test cycles."""

    issue_count: int = field(default_factory=int)
    """Number of issues associated with the test cycle."""

    issue_key: str = field(default_factory=str)
    """Related Jira issue that the test cycle is associated with."""

    key: str = field(default_factory=str)
    """Test cycle key (eg: MYPROJECT-C123)."""

    name: str = field(default_factory=str)
    """Name of the test cycle."""

    owner: str = field(default_factory=str)
    """User that owns the test cycle."""

    planned_end_date: datetime.datetime = None
    """Date and time that the test cycle is expected to finish."""

    planned_start_date: datetime.datetime = None
    """Date and time that the test cycle is expected to commence."""

    project_key: str = field(default_factory=str)
    """Project key of the project that the test cycle belongs to (eg: MYPROJECT)."""

    status: str = 'Draft'
    """Test cycle status.

    Valid options are:
        * Not Executed
        * In Progress
        * Done
    """

    test_case_count: int = field(default_factory=int)
    """Number of test cases associated with the test cycle."""

    updated_by: str = field(default_factory=str)
    """Username of the user that last updated the test cycle."""

    updated_on: datetime.datetime = None
    """Date and time that the test cycle was last updated."""
