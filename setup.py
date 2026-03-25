from setuptools import setup, find_packages

setup(
    name="pixelengine",
    version="0.1.0",
    description="A code-first pixel art animation engine for educational videos",
    author="Akash Kumar Nayak",
    packages=find_packages(),
    install_requires=[
        "Pillow>=10.0.0",
        "numpy>=1.24.0",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Multimedia :: Video",
    ],
)
