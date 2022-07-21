# -*- coding: utf-8 -*-

from pathlib import Path
from setuptools import setup
from setuptools import find_packages

# Get pewpew version
try:
    version_path = Path(__file__).parent / "pewpew" / "VERSION"
    pewpew_version = version_path.read_text().strip()
except FileNotFoundError:
    pewpew_version = "0.0.0"

with open("requirements.txt", "r") as req:
    REQUIREMENTS = [line for line in req.read().split() if line]

print("Requirements:\n" + "\n".join(REQUIREMENTS))
with open("README.md", encoding="utf-8") as readme:
    LONG_DESCRIPTION = readme.read()


def do_setup():
    setup(
        name="pewpew",
        version=pewpew_version,
        description="Cool pythonic utilities for safer, more efficient development",
        author="Taylor G Smith",
        author_email=[
            "taylor.smith@alkaline-ml.com",
        ],
        license="MIT",
        packages=find_packages(),
        include_package_data=True,
        install_requires=REQUIREMENTS,
        python_requires=">=3.8, <4",
    )


if __name__ == "__main__":
    do_setup()
