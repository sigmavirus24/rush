"""Packaging boilerplate for our example app."""
import os
import sys

import setuptools

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))  # noqa

import limiterapp

setuptools.setup(
    version=limiterapp.__version__,
    # Presently setuptools needs package-dir defined here and in setup.cfg
    # https://github.com/pypa/setuptools/issues/1136
    package_dir={"": "src"},
)
