__author__ = "Felix Engelhardt-Schott"
from setuptools import setup, find_packages

setup(
    name="k8sEnum",
    version="0.1.0",
    description="Enumerator for K8s resources focused on security & pentesting.",
    author=__author__,
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "k8sEnum = k8s_enum.__main__:main",
        ],
    },
    install_requires=["kubernetes", "tabulate", "argparse", "requests", "termcolor"],
)
