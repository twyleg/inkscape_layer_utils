# Copyright (C) 2023 twyleg
import os
import versioneer
from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="inkscape_layer_utils",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Torsten Wylegala",
    author_email="mail@twyleg.de",
    description=("Simple library to extract and manipulate layers in inkscape SVGs"),
    license="GPL 3.0",
    keywords="inkscape svg layer utilities",
    url="https://github.com/twyleg/inkscape_layer_utils",
    packages=find_packages(),
    long_description=read("README.rst"),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "inkscape_layer_utils = inkscape_layer_utils.main:main",
        ]
    },
)
