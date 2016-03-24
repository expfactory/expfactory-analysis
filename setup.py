from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

setup(
    # Application name:
    name="expanalysis",

    # Version number (initial):
    version="0.0.0",

    # Application author details:
    author=["Vanessa Sochat","Ian Eisenberg"],
    author_email=["vsochat@stanford.edu","ieisenbe@stanford.edu "],

    # Packages
    packages=find_packages(),

    # Data files
    include_package_data=True,
    zip_safe=False,

    # Details
    url="http://www.github.com/expfactory",

    license="LICENSE",
    description="Python module for experiment factory experiment analysis.",
    keywords='analysis behavior neuroscience experiment factory',

    install_requires = ['numpy','scipy','numexpr','seaborn'],

)
