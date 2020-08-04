""" Setup file. """

from setuptools import find_packages, setup

with open("README.md", "r") as readme:
    README = readme.read()

requirements = []
with open("requirements.txt", "r") as reqs:
    for req in reqs.read().splitlines():
        requirements.append(req)

version = {}
with open("src/edolab/version.py", "r") as vers:
    exec(vers.read(), version)


setup(
    name="edolab",
    version=version["__version__"],
    description="A command line tool for running experiments with `edo`.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/daffidwilde/edolab",
    author="Henry Wilde",
    author_email="henrydavidwilde@gmail.com",
    license="MIT",
    keywords=["artificial data", "evolutionary algorithm", "experiments"],
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    install_requires=requirements,
    tests_require=["pytest", "pytest-cov", "numpy"],
    entry_points={"console_scripts": "edolab=edolab.__main__:main"},
)
