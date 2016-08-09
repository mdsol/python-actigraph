# -*- coding: utf-8 -*-
__author__ = 'iansparks'
from setuptools import setup

setup(
    name='actigraph',
    version='1.0.0',
    author='Ian Sparks',
    author_email='isparks@mdsol.com',
    packages=['actigraph'],
    url='https://github.com/mdsol/python-actigraph',
    license='MIT',
    description="A basic Actigraph client based on the requests library.",
    long_description=open('README.md').read(),
    zip_safe=False,
    include_package_data=True,
    test_suite='tests',
    package_data = { '': ['README.md'] },
    install_requires=['requests', 'six'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
