import os
from setuptools import find_packages, setup


NAME = 'inkscape_svg_layer_extractor'
VERSION = '0.0.2'

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name=NAME,
    version=VERSION,
    author="Torsten Wylegala",
    author_email="mail@twyleg.de",
    description=("Small script to extract layers from inscape svg"),
    license="GPL 3.0",
    keywords="inkscape svg layer extractor",
    url="https://github.com/twyleg",
    packages=find_packages(),
    long_description=read('README.md'),
    install_requires=[],
    cmdclass={}
)
