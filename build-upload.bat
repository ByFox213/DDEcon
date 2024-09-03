py -3.11 -m pip install -U build setuptools twine
del dist

py -3.11 -m build
py -3.11 -m twine upload dist/*
pause