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
* [Overview](#overview)
  * [Features](#features)
  * [Supported Django and Python versions](#supported-django-and-python-versions)
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


## pinax-points

### Overview

`pinax-points` is a points, positions and levels app for Django.

#### Features

`pinax-points` provides the ability to track points on arbitrary
objects in your system.  The common case being `User` instances. It can
additionally keep track of positions for these objects to produce leaderboards.

#### Supported Django and Python versions

Django \ Python | 2.7 | 3.4 | 3.5 | 3.6
--------------- | --- | --- | --- | ---
1.11 |  *  |  *  |  *  |  *  
2.0  |     |  *  |  *  |  *


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

### 0.7

* Improve usage documentation

### 0.6

* Improving tox.ini syntax
* Standardizing setup.py and docs
* Improving .gitignore

### 0.5

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

`pinax-points` was formerly known as `agon`.
The code was mostly extracted from [typewar](http://typewar.com) and made slightly more
generic to work well.


## Contribute

For an overview on how contributing to Pinax works read this [blog post](http://blog.pinaxproject.com/2016/02/26/recap-february-pinax-hangout/)
and watch the included video, or read our [How to Contribute](http://pinaxproject.com/pinax/how_to_contribute/) section.
For concrete contribution ideas, please see our
[Ways to Contribute/What We Need Help With](http://pinaxproject.com/pinax/ways_to_contribute/) section.

In case of any questions we recommend you join our [Pinax Slack team](http://slack.pinaxproject.com)
and ping us there instead of creating an issue on GitHub. Creating issues on GitHub is of course
also valid but we are usually able to help you faster if you ping us in Slack.

We also highly recommend reading our blog post on [Open Source and Self-Care](http://blog.pinaxproject.com/2016/01/19/open-source-and-self-care/).


## Code of Conduct

In order to foster a kind, inclusive, and harassment-free community, the Pinax Project
has a [code of conduct](http://pinaxproject.com/pinax/code_of_conduct/).
We ask you to treat everyone as a smart human programmer that shares an interest in Python, Django, and Pinax with you.


## Connect with Pinax

For updates and news regarding the Pinax Project, please follow us on Twitter [@pinaxproject](https://twitter.com/pinaxproject)
and check out our [Pinax Project blog](http://blog.pinaxproject.com).


## License

Copyright (c) 2012-2018 James Tauber and contributors under the [MIT license](https://opensource.org/licenses/MIT).
