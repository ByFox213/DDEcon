import asyncio

from ddecon import AsyncECON


async def main():
    econ = AsyncECON("127.0.0.1", 12345, "password")
    await econ.connect()
    await econ.message("Hello, world!")
    while True:
        message = await econ.read()
        if message is not None:
            print(message.decode()[:-3])


asyncio.run(main())
