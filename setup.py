"""Minimal setup.py for editable development installs."""
from setuptools import setup, find_packages

setup(
    name="pixelengine",
    version="0.3.0",
    packages=find_packages(include=["pixelengine*"]),
)
