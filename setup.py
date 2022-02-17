import os
from setuptools import setup

from beschi import LIB_VERSION, LIB_NAME

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md')) as f:
    DESC = f.read()

setup(
    name=LIB_NAME,
    version=LIB_VERSION,
    description='code generator for binary message passing between languages',
    long_description=DESC,
    url='https://github.com/sjml/beschi',
    author='Shane Liesegang',
    license='MIT',
    classifier=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
    ],
    packages=['beschi'],
    install_requires=[
        'toml',
    ],
    extras_require={
        'dev': [
            'pytest'
        ]
    },
    entry_points={
        'console_scripts': [
            'beschi = beschi.cli:main'
        ]
    }
)
