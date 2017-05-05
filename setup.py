#!/usr/bin/env python
# coding=utf-8

from distutils.core import setup

# noinspection PyArgumentList
setup(
    name='alignment',
    version='1.0.10',
    author='Eser Aygün',
    author_email='eser.aygun@gmail.com',
    packages=['alignment'],
    url='https://github.com/eseraygun/python-alignment',
    license='BSD 3-Clause License',
    description='Native Python library for generic sequence alignment.',
    long_description=open('README.rst').read(),
    requires=['numpy', 'six'],
)
