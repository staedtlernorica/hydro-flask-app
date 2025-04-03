# setup.py
from setuptools import setup, find_packages

setup(
    name="tohydroviz",  # The name of your package
    version="0.1",      # The version of your package
    packages=find_packages(),  # Automatically find your package
    install_requires=[],  # List any dependencies here
    test_suite="tests",   # Define where your test files are located
    author="Long Vuong",   # Your name
    author_email="longvuong@live.com",  # Your email
    description="A description of your package",  # Short description
    long_description=open('README.md').read(),  # Long description (from README)
    long_description_content_type="text/markdown",  # Content type of README
    url="https://github.com/staedtlernorica/hydro-flask-app",  # Link to the project (if applicable)
)