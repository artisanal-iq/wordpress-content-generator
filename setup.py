#!/usr/bin/env python3
"""
Setup script for WordPress Content Generator

This script installs the WordPress Content Generator package and its dependencies.
It also creates command-line entry points for the agent runner and orchestrator.
"""

import os
from setuptools import setup, find_packages

# Read the content of README.md for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="wordpress-content-generator",
    version="0.1.0",
    author="Jay Jordan",
    author_email="jay@example.com",
    description="An autonomous, agent-based system that generates and publishes WordPress content",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/artisanal-iq/wordpress-content-generator",
    packages=find_packages(exclude=["tests", "docs"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "run-agent=run_agent:main",
            "orchestrator=orchestrator:main",
            "seed-data=seed_data:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md", "*.sql"],
    },
    zip_safe=False,
)
