#!/usr/bin/env python3
"""Setup script for DB-Forge Python client library."""

from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="dbforge-client",
    version="1.0.0",
    description="Python client library for Praetorian DB-Forge",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Praetorian DB-Forge Team",
    author_email="contact@dbforge.dev",
    url="https://github.com/praetorian/db-forge-mk1",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.8.0",
        "typing-extensions>=4.0.0; python_version<'3.10'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "mypy>=0.991",
        ],
    },
    entry_points={
        "console_scripts": [
            "dbforge=dbforge_client.cli:main",
        ],
    },
)