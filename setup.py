from distutils.core import setup


setup(
    name = "agon",
    version = "0.1.dev19",
    author = "Eldarion",
    author_email = "development@eldarion.com",
    description = "a reusable Django points, positions and levels application",
    long_description = open("README.rst").read(),
    license = "BSD",
    url = "http://github.com/eldarion/agon",
    packages = [
        "agon",
        "agon.templatetags",
    ],
    package_data = {
        "agon": [
            "templates/agon/*.html",
            "templates/admin/agon/awardedpointvalue/*.html",
        ]
    },
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ]
)
