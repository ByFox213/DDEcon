import asyncio
import os

from ddecon import AsyncECON


async def main():
    econ = AsyncECON(os.getenv("econ_ip"), int(os.getenv("econ_port")), os.getenv("econ_password"))
    await econ.connect()
    await econ.message("Hello, world!")
    while True:
        message = await econ.read()
        if message is None:
            continue
        print(message.decode()[:-3])


asyncio.run(main())
