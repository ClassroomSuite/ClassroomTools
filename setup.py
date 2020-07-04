from setuptools import setup, find_packages, find_namespace_packages

with open('requirements.txt') as f:
    requirements = list(f.read().splitlines())

setup(
    name='classroom_tools',
    packages=find_packages(),
    install_requires=requirements
)
