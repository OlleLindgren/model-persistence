import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements=[]

setuptools.setup(
    name="model_persistence",
    version="v0.1.1",
    author="Olle Lindgren",
    author_email="lindgrenolle@live.se",
    description="A package for manaing model persistence",
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
