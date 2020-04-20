![](http://pinaxproject.com/pinax-design/patches/pinax-points.svg)

# Pinax Points

[![](https://img.shields.io/pypi/v/pinax-points.svg)](https://pypi.python.org/pypi/pinax-points/)

[![CircleCi](https://img.shields.io/circleci/project/github/pinax/pinax-points.svg)](https://circleci.com/gh/pinax/pinax-points)
[![Codecov](https://img.shields.io/codecov/c/github/pinax/pinax-points.svg)](https://codecov.io/gh/pinax/pinax-points)
[![](https://img.shields.io/github/contributors/pinax/pinax-points.svg)](https://github.com/pinax/pinax-points/graphs/contributors)
[![](https://img.shields.io/github/issues-pr/pinax/pinax-points.svg)](https://github.com/pinax/pinax-points/pulls)
[![](https://img.shields.io/github/issues-pr-closed/pinax/pinax-points.svg)](https://github.com/pinax/pinax-points/pulls?q=is%3Apr+is%3Aclosed)

[![](http://slack.pinaxproject.com/badge.svg)](http://slack.pinaxproject.com/)
[![](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)


## Table of Contents

* [About Pinax](#about-pinax)
* [Important Links](#important-links)
* [Overview](#overview)
  * [Features](#features)
  * [Supported Django and Python Versions](#supported-django-and-python-versions)
* [Documentation](#documentation)
  * [Installation](#installation)
  * [Usage](#usage)
  * [Signals](#signals)
  * [Template Tags](#template-tags)
* [Change Log](#change-log)
* [History](#history)
* [Contribute](#contribute)
* [Code of Conduct](#code-of-conduct)
* [Connect with Pinax](#connect-with-pinax)
* [License](#license)


## About Pinax

Pinax is an open-source platform built on the Django Web Framework. It is an ecosystem of reusable
Django apps, themes, and starter project templates. This collection can be found at http://pinaxproject.com.


## Important Links

Where you can find what you need:
* Releases: published to [PyPI](https://pypi.org/search/?q=pinax) or tagged in app repos in the [Pinax GitHub organization](https://github.com/pinax/)
* Global documentation: [Pinax documentation website](https://pinaxproject.com/pinax/)
* App specific documentation: app repos in the [Pinax GitHub organization](https://github.com/pinax/)
* Support information: [SUPPORT.md](https://github.com/pinax/.github/blob/master/SUPPORT.md) file in the [Pinax default community health file repo](https://github.com/pinax/.github/)
* Contributing information: [CONTRIBUTING.md](https://github.com/pinax/.github/blob/master/CONTRIBUTING.md) file in the [Pinax default community health file repo](https://github.com/pinax/.github/)
* Current and historical release docs: [Pinax Wiki](https://github.com/pinax/pinax/wiki/)


## pinax-points

### Overview

`pinax-points` is a points, positions and levels app for Django.

#### Features

`pinax-points` provides the ability to track points on arbitrary
objects in your system.  The common case being `User` instances. It can
additionally keep track of positions for these objects to produce leaderboards.

#### Supported Django and Python Versions

Django / Python | 3.6 | 3.7 | 3.8
--------------- | --- | --- | ---
2.2  |  *  |  *  |  *
3.0  |  *  |  *  |  *


## Documentation

### Installation

To install pinax-points:

```shell
    $ pip install pinax-points
```

Add `pinax.points` to your `INSTALLED_APPS` setting:

```python
    INSTALLED_APPS = [
        # other apps
        "pinax.points",
    ]
```

### Usage

#### Setting and Getting Points

##### `award_points(target, value, reason="", source=None)`

Award points to any model instance by invoking `award_points()`. 

```python
    from pinax.points.models import award_points
    
    award_points(user, 50)
```

##### `points_awarded(target)`

Obtain points awarded based on argument criteria.

```python
    from pinax.points.models import points_awarded
    
    points = points_awarded(user)
```

#### Template Display

To display overall points for an object, use templatetag `points_for_object` to set and display a context variable:

```django
    {% load pinax_points_tags %}
    
    {% points_for_object user as points %}
    <div class="user-points">{{ points }}</div>
```
    
Although this example shows points for a User, any type of model instance is valid.
For example if you want to display points for a blog post:

```django
    {% load pinax_points_tags %}
    
    {% points_for_object post as points %}
    <div class="post-points">{{ points }}</div>
```

#### Signals

##### `points_awarded`

Triggered when points are awarded to an object.

    providing_args=["target", "key", "points", "source"]

#### Template Tags

##### `points_for_object`

Returns the current points for an object.

Usage:

```django
    {% points_for_object user %}
```

  or

```django
    {% points_for_object user as points %}
```

  or
  
```django
    {% points_for_object user limit 7 days as points %}
```

##### `top_objects`

Returns a queryset of the model passed in with points annotated.

Usage:

```django
    {% top_objects "auth.User" as top_users limit 10 %}
```

  or
```django
    {% top_objects "auth.User" as top_users %}
```

  or
  
```django
    {% top_objects "auth.User" as top_users limit 10 timeframe 7 days %}
```

##### `user_has_voted`

Returns True if `user` has voted on `obj`, False otherwise.

Usage:

```django
    {% user_has_voted user obj as var %}
```

## Change Log

### 2.0

* Drop Django 1.11, 2.0, and 2.1, and Python 2,7, 3.4, and 3.5 support
* Add Django 2.2 and 3.0, and Python 3.6, 3.7, and 3.8 support
* Update packaging configs
* Direct users to community resources

### 1.0

* Improve usage documentation
* Improving tox.ini syntax
* Standardizing setup.py and docs
* Improving .gitignore
* Standardize documentation layout
* Drop Django v1.8, 1.9, 1.10 support
* Drop Python 3.3 support
* Add Django 2.0 support
* Move documentation into README.md
* Convert CI and coverage to CircleCi and CodeCov
* Add PyPi-compatible long description

### 0.4

- updated to 

### 0.3

### 0.1


## History

`pinax-points` was formerly known as `agon`. The code was mostly extracted from [typewar](http://typewar.com) and made slightly more
generic to work well.


## Contribute

[Contributing](https://github.com/pinax/.github/blob/master/CONTRIBUTING.md) information can be found in the [Pinax community health file repo](https://github.com/pinax/.github).


## Code of Conduct

In order to foster a kind, inclusive, and harassment-free community, the Pinax Project has a [Code of Conduct](https://github.com/pinax/.github/blob/master/CODE_OF_CONDUCT.md). We ask you to treat everyone as a smart human programmer that shares an interest in Python, Django, and Pinax with you.


## Connect with Pinax

For updates and news regarding the Pinax Project, please follow us on Twitter [@pinaxproject](https://twitter.com/pinaxproject) and check out our [Pinax Project blog](http://blog.pinaxproject.com).


## License

Copyright (c) 2012-present James Tauber and contributors under the [MIT license](https://opensource.org/licenses/MIT).
