import os
from setuptools import setup, find_packages

from beschi import LIB_VERSION, LIB_NAME

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md')) as f:
    DESC = f.read()

setup(
    name=LIB_NAME.lower(),
    version=LIB_VERSION,
    description='bit-packing and unpacking code generator for C#, Go, and TypeScript',
    long_description=DESC,
    long_description_content_type='text/markdown',
    url='https://github.com/sjml/beschi',
    author='Shane Liesegang',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
    ],
    packages=find_packages(
        include=['beschi', 'beschi.writers'],
        exclude=['test'], # seems to include test no matter what. ¯\_(ツ)_/¯
    ),
    install_requires=[
        'toml',
    ],
    extras_require={
        'dev': [
            'pytest',
            'build',
            'twine'
        ]
    },
    entry_points={
        'console_scripts': [
            'beschi = beschi.cli:main'
        ]
    }
)
