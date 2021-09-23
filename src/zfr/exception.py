"""ZFR exceptions."""


class AuthorizationError(PermissionError):
    """Raised when the user is not permitted to perform an action."""

    def __init__(self, message: str) -> None:
        """Initialize a new AuthorizationError object."""
        self.message = message
        super().__init__(self.message)
