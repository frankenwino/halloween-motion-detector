#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "gpiozero",
    "picamera"
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='halloween_motion_detector',
    version='0.1.0',
    description="Detects motion using PIR. Plays an mp3 and records video when motion is detected.",
    long_description=readme + '\n\n' + history,
    author="Andy Browne",
    author_email='andy.maildrop@gmail.com',
    url='https://github.com/frankenwino/halloween_motion_detector',
    packages=[
        'halloween_motion_detector',
    ],
    package_dir={'halloween_motion_detector':
                 'halloween_motion_detector'},
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='halloween_motion_detector',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
