# Inkscape svg layer extractor

Small script to extract layers from inscape svg

## Setup environment

To setup a development environment and install all requirements run the following commands (example for windows):

    python -m venv venv
    venv/Scripts/activate
    python -m pip install -r requirements.txt

## Build and deploy

### Build

    python setup.py sdist bdist_wheel

### Deploy

TestPyPI:

    python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
    
PyPi:

    python -m twine upload dist/*