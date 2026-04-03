"""Minimal setup.py for editable development installs."""
from setuptools import setup, find_packages

setup(
    name="pixelengine",
    version="0.9.0",
    packages=find_packages(include=["pixelengine*"]),
    install_requires=[
        "Pillow",
        "numpy",
        "svgelements",
        "matplotlib",
    ],
    extras_require={
        "perf": ["av", "pymunk", "pydub"],
        "av": ["av"],
        "physics": ["pymunk"],
        "audio": ["pydub"],
    },
)
