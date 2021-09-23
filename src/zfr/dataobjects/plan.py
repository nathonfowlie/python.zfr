"""Data objects used to manage test plans."""

import datetime

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from zfr.dataobjects import Comment
from zfr.dataobjects.cycle import TestCycle


@dataclass(frozen=True)
class Attachment:
    """Represents a file attachment on a test plan, cycle or case.

    _See Also_:
        [Plan][zfr.dataobjects.plan.Plan]
    """

    id: int = field(default_factory=int)
    """Unique identifier for the attachment."""

    url: str = field(default_factory=str)
    """Url that the attachment can be downloaded from."""

    filename: str = field(default_factory=str)
    """Name of the attached file."""

    filesize: int = field(default_factory=int)
    """Attachment file size (in bytes)."""


@dataclass
class Plan:
    """Represents an existing test plan.

    _See Also_:
        [Attachment][zfr.dataobjects.plan.Attachment],
        [Comment][zfr.dataobjects.Comment],
        [TestCycle][zfr.dataobjects.cycle.TestCycle],
        [PlanCreate][zfr.dataobjects.plan.PlanCreate],
        [PlanUpdate][zfr.dataobjects.plan.PlanUpdate]
    """

    attachments: Optional[List[Attachment]]= field(default_factory=list)
    """List of attachments added to the test plan."""

    comments: Optional[List[Comment]] = field(default_factory=list)
    """List of comments added by users."""

    created_by: str = field(default_factory=str)
    """Username of the user that created the plan."""

    created_on: datetime.datetime = None
    """Date and time that the plan was created."""

    custom_fields: Optional[Dict[str, str]] = field(default_factory=dict)
    """Custom fields associated with the plan, used to additional metadata."""

    folder: str = field(default_factory=str)
    """Folder used to logically group plans."""

    issue_links: Optional[List[str]] = field(default_factory=list)
    """Jira issues that are associated with the plan."""

    key: str = field(default_factory=str)
    """Unique key for the plan. (eg: MYPROJECT-P29)."""

    labels: Optional[List[str]] = field(default_factory=list)
    """Additional labels that can be used to filter plans."""

    name: str = field(default_factory=str)
    """Name of the plan."""

    objective: str = field(default_factory=str)
    """Plan objective(s).

    ???+ note "HTML"
         This field can accept basic HTML to format test (bold, italic,
         underline, links, paragraphs).
    """

    owner: str = field(default_factory=str)
    """Username of the user responsible for maintaining the test plan."""

    project_key: str = field(default_factory=str)
    """Project key oof the jira project the plan relates to. (eg: MYPROJECT)."""

    status: str = field(default_factory=str)
    """Indicates whether the test plan has been approved for use.

    Valid values are:
        - Draft
        - Approved
        - Deprecated
    """

    test_runs: Optional[List[TestCycle]] = field(default_factory=list)
    """Historical list of test cycles executed against the test plan."""

    updated_by: str = field(default_factory=str)
    """Username of the user that last updated the test plan."""

    updated_on: datetime.datetime = None
    """Date and time that the test plan was last updated."""


@dataclass
class PlanCreate:
    """Used to create a new test plan.

    _See Also_:
        [Comment][zfr.dataobjects.Comment],
        [TestCycle][zfr.dataobjects.cycle.TestCycle],
        [Plan][zfr.dataobjects.plan.Plan],
        [PlanUpdate][zfr.dataobjects.plan.PlanUpdate]
    """

    attachments: Optional[List[str]] = field(default_factory=list)
    """List of attachments added to the test plan."""

    custom_fields: Optional[Dict[str, str]] = field(default_factory=dict)
    """Custom fields associated with the plan, used to additional metadata."""

    folder: str = field(default_factory=str)
    """Folder used to logically group plans."""

    issue_links: Optional[List[str]] = field(default_factory=list)
    """Jira issues that are associated with the plan."""

    labels: Optional[List[str]] = field(default_factory=list)
    """Additional labels that can be used to filter plans."""

    name: str = field(default_factory=str)
    """Name of the plan."""

    objective: str = field(default_factory=str)
    """Plan objective(s).

    ???+ note "HTML"
         This field can accept basic HTML to format test (bold, italic,
         underline, links, paragraphs).
    """

    owner: str = field(default_factory=str)
    """Username of the user responsible for maintaining the test plan."""

    project_key: str = field(default_factory=str)
    """Project key oof the jira project the plan relates to. (eg: MYPROJECT)."""

    status: str = field(default_factory=str)
    """Indicates whether the test plan has been approved for use.

    Valid values are:
        - Draft
        - Approved
        - Deprecated
    """

    test_run_keys: Optional[List[str]] = field(default_factory=list)
    """Historical list of test cycles executed against the test plan."""


@dataclass
class PlanUpdate:
    """Used to update an existing test plan.

    _See Also_:
        [Attachment][zfr.dataobjects.plan.Attachment],
        [Comment][zfr.dataobjects.Comment],
        [TestCycle][zfr.dataobjects.cycle.TestCycle],
        [Plan][zfr.dataobjects.plan.Plan],
        [PlanCreate][zfr.dataobjects.plan.PlanCreate]
    """

    attachments: Optional[List[str]] = field(default_factory=list)
    """List of attachments added to the test plan."""

    custom_fields: Optional[Dict[str, str]] = field(default_factory=dict)
    """Custom fields associated with the plan, used to additional metadata."""

    folder: str = field(default_factory=str)
    """Folder used to logically group plans."""

    issue_links: Optional[List[str]] = field(default_factory=list)
    """Jira issues that are associated with the plan."""

    key: str = field(default_factory=str)
    """Test plan key (eg: MYPROJECT-P24)."""

    labels: Optional[List[str]] = field(default_factory=list)
    """Additional labels that can be used to filter plans."""

    name: str = field(default_factory=str)
    """Name of the plan."""

    objective: str = field(default_factory=str)
    """Plan objective(s).

    ???+ note "HTML"
         This field can accept basic HTML to format test (bold, italic,
         underline, links, paragraphs).
    """

    owner: str = field(default_factory=str)
    """Username of the user responsible for maintaining the test plan."""

    status: str = field(default_factory=str)
    """Indicates whether the test plan has been approved for use.

    Valid values are:
        - Draft
        - Approved
        - Deprecated
    """

    test_runs: Optional[List[str]] = field(default_factory=list)
    """Historical list of test cycles executed against the test plan."""
