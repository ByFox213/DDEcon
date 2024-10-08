import asyncio
import socket
from typing import Union

from .econ import ECON
from .exceptions import AlreadyConnected, AlreadyDisconnected, WrongPassword, Disconnected, ECONError


__all__ = ("AsyncECON", )


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

        try:
            await asyncio.create_task(self._connect())
        except asyncio.CancelledError:
            raise AlreadyConnected("econ: already connected")

    async def _connect(self) -> None:
        self.reader, self.writer = await asyncio.open_connection(self.ip, self.port)

        # read out useless info
        try:
            await asyncio.wait_for(self.reader.read(1024), timeout=2)
        except asyncio.TimeoutError:
            raise ECONError(f"Timeout to {self.ip}")
        except socket.error as e:
            self.writer.close()
            raise e

        await asyncio.gather(*[
            self._send_password(),
            self._read_response()
        ])

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

    async def write(self, buf: bytes) -> None:
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

    async def message(self, message: str) -> None:
        lines = message.split("\n")
        if len(lines) > 1:
            await asyncio.gather(*[
                asyncio.create_task(self._write_message(line))
                for line in lines
            ])
            return
        return await self._write_message(message)

    async def _write_message(self, message: str) -> None:
        try:
            await self.write(f"say \"{message}\"".encode())
        except Disconnected:
            raise
