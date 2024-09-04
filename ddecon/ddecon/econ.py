import asyncio
import socket
from typing import Union, Any, Coroutine

from ddecon.exceptions import AlreadyConnected, AlreadyDisconnected, WrongPassword, Disconnected


class ECON:
    def __init__(self, ip, port: int = 8303, password: str = None, auth_message: bytes = None) -> None:
        self.connected = False
        self.conn = None
        self.ip = ip
        self.port = port
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

    def write(self, buf) -> None:
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
            buffer = self.conn.recv(8192)
        except socket.error as e:
            raise e

        return buffer

    def message(self, message) -> None:
        lines = message.split("\n")
        if len(lines) > 1:
            try:
                self.write(f"say \"{lines[0]}\"".encode())
            except Disconnected:
                raise

            for line in lines[1:]:
                try:
                    self.write(f"say \"> {line}\"".encode())
                except Disconnected:
                    raise
            return
        try:
            self.write(f"say \"{message}\"".encode())
        except Disconnected:
            raise
        return


class AsyncECON(ECON):
    def __init__(self, ip, port: int = 8303, password: str = None, auth_message: bytes = None) -> None:
        super().__init__(ip, port, password, auth_message)
        self.reader = None
        self.writer = None
        self.queue = asyncio.Queue()

    async def is_connected(self) -> bool:
        return self.connected

    async def connect(self) -> None:
        if self.connected:
            raise AlreadyConnected("econ: already connected")

        task = asyncio.create_task(self._connect())
        try:
            await task
        except asyncio.CancelledError:
            raise AlreadyConnected("econ: already connected")

    async def _connect(self) -> None:
        try:
            self.reader, self.writer = await asyncio.open_connection(self.ip, self.port)
        except socket.error as e:
            raise e

        # read out useless info
        try:
            await asyncio.wait_for(self.reader.read(1024), timeout=2)
        except asyncio.TimeoutError:
            pass
        except socket.error as e:
            self.writer.close()
            raise e

        tasks = [
            self._send_password(),
            self._read_response()
        ]
        await asyncio.gather(*tasks)

        self.connected = True

    async def _send_password(self) -> None:
        try:
            self.writer.write(self.password.encode() + b"\n")
            await self.writer.drain()
        except socket.error as e:
            self.writer.close()
            raise e

    async def _read_response(self) -> None:
        try:
            buf = await asyncio.wait_for(self.reader.read(1024), timeout=2)
        except asyncio.TimeoutError:
            self.writer.close()
            raise WrongPassword("econ: wrong password")
        except socket.error as e:
            self.writer.close()
            raise e

        if self.auth_message not in buf:
            self.writer.close()
            raise WrongPassword("econ: wrong password")

    async def disconnect(self) -> None:
        if not self.connected:
            raise AlreadyDisconnected("econ: already disconnected")

        try:
            self.writer.close()
        except socket.error as e:
            raise e

        self.reader = None
        self.writer = None
        self.connected = False

    async def write(self, buf) -> None:
        if not self.connected:
            raise Disconnected("econ: disconnected")

        try:
            self.writer.write(buf + b"\n")
            await self.writer.drain()
        except socket.error as e:
            raise e

    async def read(self) -> Union[bytes, None]:
        # "ping" socket
        try:
            await self.write(b"")
        except Disconnected:
            raise

        try:
            buffer = await asyncio.wait_for(self.reader.read(8192), timeout=2)
        except socket.timeout:
            return
        except socket.error as e:
            raise e

        return buffer

    async def message(self, message) -> None:
        lines = message.split("\n")
        if len(lines) > 1:
            tasks = []
            for line in lines:
                task = asyncio.create_task(self._write_message(line))
                tasks.append(task)
            await asyncio.gather(*tasks)
        else:
            await self._write_message(message)

    async def _write_message(self, message) -> None:
        try:
            await self.write(f"say \"{message}\"".encode())
        except Disconnected:
            raise
