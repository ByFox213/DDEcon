class ECONError(Exception):
    """Base class for ECON exceptions."""
    pass


class AlreadyConnected(ECONError):
    """Raised when trying to connect an already connected ECON."""
    pass


class AlreadyDisconnected(ECONError):
    """Raised when trying to disconnect an already disconnected ECON."""
    pass


class Disconnected(ECONError):
    """Raised when trying to use a disconnected ECON."""
    pass


class WrongPassword(ECONError):
    """Raised when the password is incorrect."""
    pass
