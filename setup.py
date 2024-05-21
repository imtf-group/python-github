#!/usr/bin/env python3
from setuptools import setup


setup(
    name="python-github",
    version="0.0.1",
    author="Jean-Baptiste Langlois",
    author_email="jean-baptiste.langlois@imtf.com",
    description="Module to interface with GitHub API",
    url="https://github.com/imtf-group/python-github.git",
    packages=['github'],
    package_dir={'github': 'github'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests==2.32.0'
    ]
)
