from setuptools import find_packages, setup
from os import path
import re

name = "DevOps-metrics";
here = path.abspath(path.dirname(__file__));

with open(path.join(here, name, "__init__.py"), encoding="utf-8") as f:
    result = re.search(r'__version__ = ["\']([^"\']+)', f.read())

    if not result:
        raise ValueError("Can't find the version in kedro/__init__.py")

    version = result.group(1)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read();

# get the dependencies and installs
with open("requirements.txt", encoding="utf-8") as f:
    requires = [x.strip() for x in f if x.strip()];

# get test dependencies and installs
with open("test_requirements.txt", encoding="utf-8") as f:
    test_requires = [x.strip() for x in f if x.strip() and not x.startswith("-r")]

setup(
    name=name,
    version=version,
    description="DevOps metrics let you agregate data from multiple sources",
    license="Apache Software License (Apache 2.0)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devops-opensource/devops-metrics",
    python_requires=">=3.7, <3.11",
    packages=find_packages(exclude=["docs*", "tests*", "tools*"]),
    include_package_data=True,
    tests_require=test_requires,
    install_requires=requires,
    author="Kedro",
    package_data={
        name: ["py.typed", "test_requirements.txt"]
    },
    zip_safe=False,
    keywords="pipelines, machine learning, data pipelines, data science, data engineering",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6"
)