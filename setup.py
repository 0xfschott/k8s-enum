__author__ = "Felix Engelhardt-Schott"
import os
from setuptools import setup, Extension, find_packages

setup(
    name="k8s-enum",
    version="0.1.0",
    description="Enumerator for K8s resources focused on security & pentesting.",
    author=__author__,
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "k8s-enum = k8s_enum.__main__:main",
        ],
    },
    install_requires=["kubernetes", "tabulate", "argparse", "requests", "termcolor"],
)
