#!/usr/bin/env python

"""The setup script."""
from requirements import *
from setuptools import setup, find_packages

with open('README.rst', 'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

setup(
    name='clean_architecture_mongodb_adapter',
    version='0.1.0',
    author="Anselmo Lira (https://github.com/aberriel)",
    author_email="anselmo.lira1@gmail.com",
    description="Concrete implementation of adapter to MongoDB",
    url='https://github.com/aberriel/clean_architecture_mongodb_adapter',
    packages=find_packages(include=['clean_architecture_mongodb_adapter', 'clean_architecture_mongodb_adapter.*']),
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
    ],
    entry_points={
        'console_scripts': [
            'clean_architecture_mongodb_adapter=clean_architecture_mongodb_adapter.cli:main',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='clean_architecture_mongodb_adapter',
    test_suite='tests',
    zip_safe=False,
)
