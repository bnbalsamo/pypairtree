from setuptools import setup, find_packages


def readme():
    with open("README.md", 'r') as f:
        return f.read()


setup(
    name="pypairtree",
    description="A python package for creating and manipulating pairtrees.",
    version="0.0.1",
    long_description=readme(),
    author="Brian Balsamo",
    author_email="brian@brianbalsamo.com",
    packages=find_packages(
        exclude=[
        ]
    ),
    entry_points={
        'console_scripts': [
            'ppath_to_id = pypairtree.utils:path_to_id_app',
            'id_to_ppath = pypairtree.utils:id_to_path_app'
        ]
    },
    include_package_data=True,
    url='https://github.com/bnbalsamo/pypairtree',
    install_requires=[
    ],
    tests_require=[
        'pytest'
    ],
    test_suite='tests'
)
