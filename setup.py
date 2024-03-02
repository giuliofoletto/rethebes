"""
Setup file to install rethebes as a package.

Usage: pip install .

Authors: Giulio Foletto.
"""

from setuptools import setup

# Assign the content of README.md to long_description
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='rethebes',
      version='0.1.0',
      description='Repeatable thermal benchmarks',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Giulio Foletto',
      author_email='giulio.foletto@outlook.com',
      packages=['rethebes'],
      package_dir={'rethebes': 'rethebes'},
      install_requires=[
          'psutil',
          'pythonnet'
      ],
      entry_points={'console_scripts': ['rethebes = rethebes.__main__:cli']},
      zip_safe=False)
