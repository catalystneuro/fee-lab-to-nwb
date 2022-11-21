# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "requirements.txt")) as f:
    install_requires = f.read().strip().split("\n")

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="fee-lab-to-nwb",
    version="1.1.0",
    description="NWB conversion scripts, functions, and classes for the Fee lab.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ben Dichter, Cody Baker, and Szonja Weigl",
    author_email="ben.dichter@catalystneuro.com",
    url="https://github.com/catalystneuro/fee-lab-to-nwb",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=install_requires,
)
