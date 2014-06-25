# -*- coding: utf-8 -*-
__author__ = 'iansparks'
from setuptools import setup

setup(
    name='actigraph',
    version='0.0.1',
    author='Ian Sparks',
    author_email='isparks@mdsol.com',
    packages=['actigraph'],
    url='https://github.com/mdsol/python-actigraph',
    license='MIT',
    description="A basic Actigraph client based on the requests library.",
    long_description=open('README.md').read(),
    zip_safe=False,
    include_package_data=True,
    package_data = { '': ['README.md'] },
    install_requires=['requests'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
