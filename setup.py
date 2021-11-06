import setuptools
from pathlib import Path

src_root = Path(__file__).parent

with open(src_root / "README.md", "r") as f:
    long_description = f.read()

requirements = []

with open(src_root / '__init__.py', "r") as f:
    __version_line = next(filter(lambda s: 'version' in s, f.readlines()))
    version = __version_line.split('=')[-1].strip(" \n\"")

setuptools.setup(
    name="model_persistence",
    version=version,
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
    python_requires='>=3.0',
)
