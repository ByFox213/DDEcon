python -m pip install -U build setuptools twine
rm -rf dist

python -m build
python -m twine upload dist/*