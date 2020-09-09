#!/usr/bin/env python3
"""Setup the Traiter environment."""

import re
from distutils.core import setup

from setuptools import find_packages

DESCRIPTION = """Traiter"""


def readme():
    """Get README.md content."""
    with open('README.md') as in_file:
        return in_file.read()


def license_():
    """Get LICENSE.txt content."""
    with open('LICENSE') as in_file:
        return in_file.read()


def find_version():
    """Read version from db.py."""
    regex = r"""^__VERSION__ = ['"]v?([^'"]*)['"]"""
    with open('traiter/pylib/util.py') as in_file:
        match = re.search(regex, in_file.read(), re.M)
        if match:
            return match.group(1)

    raise RuntimeError('Unable to find version string.')


def find_requirements():
    """Read requirements.txt file and returns list of requirements."""
    with open('requirements.txt') as in_file:
        return in_file.read().splitlines()


setup(
    name='traiter',
    version=find_version(),
    packages=find_packages(),
    install_requires=find_requirements(),
    description=DESCRIPTION,
    long_description=readme(),
    license=license_(),
    url='https://github.com/rafelafrance/traiter',
    python_requires='>=3.8',
    scripts=[])
