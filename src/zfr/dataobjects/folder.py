"""Data objects used to manage Zephyr folders."""

from dataclasses import dataclass, field
from enum import Enum


class FolderType(str, Enum):
    """Zephyr folder type.

    _See Also_:
        [Folder][zfr.dataobjects.Folder]
    """

    CASE = 'TEST_CASE'
    """Indicates that the folder should be used to group test cases."""

    CYCLE = 'TEST_RUN'
    """Indicates that the folder should be used to group test cycles."""

    PLAN = 'TEST_PLAN'
    """Indicates that the folder should be used to group test plans."""

    def __str__(self) -> str:
        """Enum key value.

        Returns:
           The enum value expressed as a string.
        """
        return str(self.value)


@dataclass
class Folder:
    """Represents a Zephyr folder.

    _See Also_:
        [FolderType][zfr.dataobjects.FolderType]
    """

    def __init__(
        self,
        id: int = 0,
        name: str = None,
        type: FolderType = FolderType.PLAN
    ) -> None:
        """Initialize a Folder object.

        Args:
            id: Unique id of the existing folder.
            name: Name of the folder.
            type: Type of test data associated with the folder (Test Plan,
                Test Cycle or Test Case).
        """
        self.id = id
        self.name = name if name.startswith('/') else f"/{name}"
        self.type = type

    id: int = field(default_factory=int)
    """Unique id of the folder."""

    name: str = field(default_factory=str)
    """Folder name.

    ???+ note "Naming Conventions"
         The Zephyr API is a little inconsistent with the way that it handles
         folder names. It expects the folder name to start with a forward slash
         when creating the folder, but requires that it doesn't start with a
         forward slash when updating the folder.

         The CLI sub-commands will attempt to hide this inconsistency as best
         as they can, to provide for a nicer user-experience.
    """

    type: FolderType = None
    """The type of test information associated with the folder.

    Valid options are:
        * TEST_PLAN
        * TEST_CYCLE
        * TEST_CASE

    _See Also_:
        [FolderType][zfr.dataobjects.folder.FolderType]
    """


@dataclass
class FolderCreate:
    """Represents a new Zephyr folder.

    _See Also_:
        [FolderType][zfr.dataobjects.FolderType],
        [Folder][zfr.dataobjects.FolderUpdate],
        [FolderUpdate][zfr.dataobjects.FolderUpdate],
    """

    name: str = field(default_factory=str)
    """Folder name.

    ???+ note "Naming Conventions"
         The Zephyr API is a little inconsistent with the way that it handles
         folder names. It expects the folder name to start with a forward slash
         when creating the folder, but requires that it doesn't start with a
         forward slash when updating the folder.

         The CLI sub-commands will attempt to hide this inconsistency as best
         as they can, to provide for a nicer user-experience.
    """

    project_key: str = field(default_factory=str)
    """Project key of the project that the folder will reside within."""

    type: FolderType = None
    """The type of test information associated with the folder.

    Valid options are:
        * TEST_PLAN
        * TEST_CYCLE
        * TEST_CASE

    _See Also_:
        [FolderType][zfr.dataobjects.folder.FolderType]
    """
