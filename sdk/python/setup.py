# sdk/python/setup.py
from setuptools import setup, find_packages

setup(
    name="persisto",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pydantic"
    ],
    author="Trusten",
    description="SDK for Persisto AI — a semantic memory API for LLM apps",
)
