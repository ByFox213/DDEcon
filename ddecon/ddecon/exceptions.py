class ECONError(Exception):
    """Base class for ECON exceptions."""

    pass


class AlreadyConnectedError(ECONError):
    """Raised when trying to connect an already connected ECON."""

    pass


class AlreadyDisconnectedError(ECONError):
    """Raised when trying to disconnect an already disconnected ECON."""

    pass


class DisconnectedError(ECONError):
    """Raised when trying to use a disconnected ECON."""

    pass


class WrongPasswordError(ECONError):
    """Raised when the password is incorrect."""

    pass
