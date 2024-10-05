import socket

from .exceptions import AlreadyConnected, AlreadyDisconnected, WrongPassword, Disconnected


__all__ = ("ECON", )


class ECON:
    def __init__(
            self,
            ip: str,
            port: int = 8303,
            password: str = None,
            auth_message: bytes = None
    ) -> None:
        self.connected = False
        self.conn = None
        self.ip = ip
        self.port = port
        self.auth_message = auth_message
        if auth_message is None:
            self.auth_message = b"Authentication successful"
        if password is None:
            raise ValueError("Password is None")
        self.password = password

    def is_connected(self) -> bool:
        return self.connected

    def connect(self) -> None:
        if self.connected:
            raise AlreadyConnected("econ: already connected")

        try:
            self.conn = socket.create_connection((self.ip, self.port), timeout=2)
        except socket.error as e:
            raise e

        # read out useless info
        try:
            self.conn.recv(1024)
        except socket.timeout:
            pass
        except socket.error as e:
            self.conn.close()
            raise e
        self.conn.settimeout(None)

        try:
            self.conn.sendall(self.password.encode() + b"\n")
        except socket.error as e:
            self.conn.close()
            raise e

        # check authentication
        self.conn.settimeout(2)
        try:
            buf = self.conn.recv(1024)
        except socket.timeout:
            self.conn.close()
            raise WrongPassword("econ: wrong password")
        except socket.error as e:
            self.conn.close()
            raise e
        self.conn.settimeout(None)

        if self.auth_message not in buf:
            self.conn.close()
            raise WrongPassword("econ: wrong password")

        self.connected = True

    def disconnect(self) -> None:
        if not self.connected:
            raise AlreadyDisconnected("econ: already disconnected")

        try:
            self.conn.close()
        except socket.error as e:
            raise e

        self.conn = None
        self.connected = False

    def write(self, buf: bytes) -> None:
        if not self.connected:
            raise Disconnected("econ: disconnected")

        try:
            self.conn.sendall(buf + b"\n")
        except socket.error as e:
            raise e

    def read(self) -> bytes:
        # "ping" socket
        try:
            self.write(b"")
        except Disconnected:
            raise

        try:
            return self.conn.recv(8192)
        except socket.error as e:
            raise e

    def message(self, message) -> None:
        lines = message.split("\n")
        if len(lines) > 1:
            map(lambda x: self.write(f"say \"> {x}\"".encode()), lines)
            return
        self.write(f"say \"{message}\"".encode())
