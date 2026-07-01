"""
Marketic - Marketing Intelligence OS

Setup configuration.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="marketic",
    version="0.1.0",
    author="Subhajit",
    author_email="",
    description="AI-native full-stack marketing operating system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Das-rebel/marketic",
    packages=find_packages(exclude=["tests", "tests.*", "docs"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Marketing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "litellm>=1.0.0",
        "openai>=1.0.0",
        "anthropic>=0.18.0",
        "sqlalchemy>=2.0.0",
        "aiosqlite>=0.19.0",
        "pandas>=2.0.0",
        "httpx>=0.25.0",
        "feedparser>=6.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.7.0",
        ],
        "twitter": ["tweepy>=4.14.0"],
        "email": ["sendgrid>=8.0.0"],
        "slack": ["slack-sdk>=3.21.0"],
        "sms": ["twilio>=8.0.0"],
        "browser": ["playwright>=1.40.0"],
    },
)
