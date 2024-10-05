python3.11 -m pip install -U build setuptools twine
rm -rf dist

python3.11 -m build
python3.11 -m twine upload dist/*