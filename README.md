## Installation

```bash
  pip install ddecon
```
    
## Usage/Examples


```python
from ddecon import ECON

if __name__ == "__main__":
    econ = ECON("127.0.0.1", 8303, "password")
    econ.connect()
    econ.message("Hello World")
    print(econ.read())
    econ.disconnect()
```

[other examples](https://github.com/ByFox213/ddecon/tree/main/examples)
