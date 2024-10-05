from ddecon import ECON

if __name__ == "__main__":
    econ = ECON("127.0.0.1", 8303, "password")
    econ.connect()
    econ.message("Hello World")
    while True:
        message = econ.read()
        if message is None:
            continue
        print(message.decode()[:-3])
