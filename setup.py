from pathlib import Path

import setuptools

SRC_ROOT = Path(__file__).parent

with open(SRC_ROOT / "README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="model_persistence",
    version="0.2.4",
    author="Olle Lindgren",
    author_email="lindgrenolle@live.se",
    description="A package for managing model persistence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OlleLindgren/datasystems",
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
