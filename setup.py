from setuptools import setup, find_packages

def readme():
    with open("README.md", 'r') as f:
        return f.read()

setup(
    name = "pypairtree",
    description = "A library for creating and manipulating pairtrees",
    long_description = readme(),
    packages = find_packages(
        exclude = [
        ]
    )
)
