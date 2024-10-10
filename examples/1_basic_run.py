import os

from ddecon import ECON

if __name__ == "__main__":
    econ = ECON(os.getenv("econ_ip"), int(os.getenv("econ_port")), os.getenv("econ_password"))
    econ.connect()
    econ.message("Hello World")
    while True:
        message = econ.read()
        if message is None:
            continue
        print(message.decode()[:-3])
