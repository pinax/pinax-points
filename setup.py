from setuptools import find_packages, setup

VERSION = "1.0"
LONG_DESCRIPTION = """
.. image:: http://pinaxproject.com/pinax-design/patches/pinax-points.svg
    :target: https://pypi.python.org/pypi/pinax-points/

============
Pinax Points
============

.. image:: https://img.shields.io/pypi/v/pinax-points.svg
    :target: https://pypi.python.org/pypi/pinax-points/

\ 

.. image:: https://img.shields.io/circleci/project/github/pinax/pinax-points.svg
    :target: https://circleci.com/gh/pinax/pinax-points
.. image:: https://img.shields.io/codecov/c/github/pinax/pinax-points.svg
    :target: https://codecov.io/gh/pinax/pinax-points
.. image:: https://img.shields.io/github/contributors/pinax/pinax-points.svg
    :target: https://github.com/pinax/pinax-points/graphs/contributors
.. image:: https://img.shields.io/github/issues-pr/pinax/pinax-points.svg
    :target: https://github.com/pinax/pinax-points/pulls
.. image:: https://img.shields.io/github/issues-pr-closed/pinax/pinax-points.svg
    :target: https://github.com/pinax/pinax-points/pulls?q=is%3Apr+is%3Aclosed

\ 

.. image:: http://slack.pinaxproject.com/badge.svg
    :target: http://slack.pinaxproject.com/
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://opensource.org/licenses/MIT/

\ 

``pinax-points`` is a points, positions and levels app for Django.

``pinax-points`` provides the ability to track points on arbitrary
objects in your system.  The common case being ``User`` instances. It can
additionally keep track of positions for these objects to produce leaderboards.

Supported Django and Python Versions
------------------------------------

+-----------------+-----+-----+-----+-----+
| Django / Python | 2.7 | 3.4 | 3.5 | 3.6 |
+=================+=====+=====+=====+=====+
|  1.11           |  *  |  *  |  *  |  *  |
+-----------------+-----+-----+-----+-----+
|  2.0            |     |  *  |  *  |  *  |
+-----------------+-----+-----+-----+-----+
"""

setup(
    author="Pinax Team",
    author_email="team@pinaxproject.com",
    description="a points, positions and levels app for Django",
    name="pinax-points",
    long_description=LONG_DESCRIPTION,
    version=VERSION,
    url="http://github.com/pinax/pinax-points/",
    license="MIT",
    packages=find_packages(),
    package_data={
        "points": [
            "templates/pinax/points/*.html",
            "templates/admin/pinax/points/awardedpointvalue/*.html",
        ]
    },
    extras_require={
        "pytest": ["pytest", "pytest-django"]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "Django>=1.11"
    ],
    tests_require=[
    ],
    test_suite="runtests.runtests",
    zip_safe=False
)
