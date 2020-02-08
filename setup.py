import sys
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))


# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mpfs2",
    version="0.0.1",
    description="Extract files from a Microchip Proprietary File System (MPFS2)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rene-d/mpfs2",
    author="Rene Devichi",
    author_email="rene.github@gmail.com",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="mpfs mpfs2",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["click"],
    entry_points={"console_scripts": ["mpfs2=mpfs2.mpfs2:main"]},
    project_urls={
        "Source": "https://github.com/rene-d/mpfs2",
        "Bug Reports": "https://github.com/rene-d/mpfs2/issues",
    },
)
