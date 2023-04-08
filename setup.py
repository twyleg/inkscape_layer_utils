# Copyright (C) 2023 twyleg
import os
from setuptools import find_packages, setup

from inkscape_layer_utils._version import __version__


NAME = 'inkscape_layer_utils'
VERSION = __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name=NAME,
    version=VERSION,
    author="Torsten Wylegala",
    author_email="mail@twyleg.de",
    description=("Simple library to extract and manipulate layers from inscape SVGs"),
    license="GPL 3.0",
    keywords="inkscape svg layer utilities",
    url="https://github.com/twyleg",
    packages=find_packages(),
    long_description=read('README.md'),
    install_requires=[],
    cmdclass={},
    entry_points={
        'console_scripts': [
            'inkscape_layer_utils = inkscape_layer_utils.main:main',
        ]
    }
)
