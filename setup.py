import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ddecon",
    version="0.2.2",
    author="ByFox",
    description="DDnet econ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ByFox213/ddecon",
    project_urls={"Github": "https://github.com/ByFox213/ddecon"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "ddecon"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.10",
)
