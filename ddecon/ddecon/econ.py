import socket

from .exceptions import (
    AlreadyConnectedError,
    AlreadyDisconnectedError,
    WrongPasswordError,
    DisconnectedError,
)


__all__ = ("ECON",)


class ECON:
    def __init__(
        self,
        ip: str,
        port: int = 8303,
        password: str = None,
        auth_message: bytes = None,
    ) -> None:
        if password is None:
            raise ValueError("Password is None")

        self.password = password
        self.auth_message = auth_message or b"Authentication successful"
        self.ip = ip
        self.port = port
        self.conn = None
        self.connected = False

    def is_connected(self) -> bool:
        return self.connected

    def connect(self) -> None:
        if self.connected:
            raise AlreadyConnectedError("econ: already connected")

        try:
            self.conn = socket.create_connection((self.ip, self.port), timeout=2)
            self.conn.recv(1024)  # read out useless info
            self.conn.sendall(self.password.encode() + b"\n")
            buf = self.conn.recv(1024)
            if self.auth_message not in buf:
                raise WrongPasswordError("econ: wrong password")
            self.conn.settimeout(None)
            self.connected = True
        except socket.error as e:
            self.conn.close()
            raise e

    def disconnect(self) -> None:
        if not self.connected:
            raise AlreadyDisconnectedError("econ: already disconnected")

        try:
            self.conn.close()
        except socket.error as e:
            raise e
        finally:
            self.conn = None
            self.connected = False

    def write(self, buf: bytes) -> None:
        if not self.connected:
            raise DisconnectedError("econ: disconnected")

        try:
            self.conn.sendall(buf + b"\n")
        except socket.error as e:
            raise e

    def read(self) -> bytes:
        try:
            self.write(b"")  # "ping" socket
        except DisconnectedError:
            raise

        try:
            return self.conn.recv(8192)
        except socket.error as e:
            raise e

    def message(self, message) -> None:
        lines = message.split("\n")
        if len(lines) > 1:
            for x in (f'say "> {x}"'.encode() for x in lines):
                self.write(x)
        else:
            self.write(f'say "{message}"'.encode())
