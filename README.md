## Installation

```bash
pip install ddecon
```
    
## Usage/Examples


sync
```python
import os

from ddecon import ECON

if __name__ == "__main__":
    econ = ECON(
        os.getenv("econ_ip"), int(os.getenv("econ_port")), os.getenv("econ_password")
    )
    econ.connect()
    econ.message("Hello World")
    while True:
        message = econ.read()
        if message is None:
            continue
        print(message.decode()[:-3])
```

async
```python
import asyncio
import os

from ddecon import AsyncECON


async def send_hello(econ):
    count = 0
    while True:
        count += 1
        await econ.message(f"Hello, world!, {count}")
        await asyncio.sleep(5)


async def main():
    econ = AsyncECON(
        os.getenv("econ_ip"), int(os.getenv("econ_port")), os.getenv("econ_password")
    )
    await econ.connect()
    asyncio.create_task(send_hello(econ))
    while True:
        message = await econ.read()
        if message is None:
            continue
        print(message.decode()[:-3])


asyncio.run(main())

```
