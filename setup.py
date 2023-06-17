# Copyright (C) 2023 twyleg
import versioneer
from pathlib import Path
from setuptools import find_packages, setup


def read(relative_filepath):
    return open(Path(__file__).parent / relative_filepath).read()


def read_long_description() -> str:
    return read("README.rst").replace(
        "docs/_static/", "https://raw.githubusercontent.com/twyleg/inkscape_layer_utils" "/master/docs/_static/"
    )


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
    long_description=read_long_description(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "inkscape_layer_utils = inkscape_layer_utils.main:main",
        ]
    },
)
