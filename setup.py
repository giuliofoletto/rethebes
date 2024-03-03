"""
Setup file to install rethebes as a package.

Usage: pip install .

Authors: Giulio Foletto.
License: See project-level license file.
"""

# Assign the content of README.md to long_description
from os import path

from setuptools import find_packages, setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="rethebes",
    version="0.1.0",
    description="Repeatable thermal benchmarks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Giulio Foletto",
    author_email="giulio.foletto@outlook.com",
    license="Apache",
    license_files=("LICENSE.txt", "NOTICE.txt"),
    packages=find_packages(),
    install_requires=["psutil", "pythonnet", "pyzmq", "pandas", "matplotlib", "numpy"],
    entry_points={"console_scripts": ["rethebes = rethebes.__main__:main"]},
    zip_safe=False,
)
