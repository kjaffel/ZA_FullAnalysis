# Dummy file to make this a package.
from setuptools import setup, find_packages

setup(
    name="run2ZAanalysis",
    description="BSM physics (implemented with bamboo)",
    url="https://github.com/kjaffel/ZA_FullAnalysis",
    author="Khawla Jaffel and Pieter David",
    author_email="khawla.jaffel@cern.ch",

    packages=find_packages("."),

    setup_requires=["setuptools_scm"],
    use_scm_version=True
)

