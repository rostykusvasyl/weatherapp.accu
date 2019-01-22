from setuptools import setup, find_namespace_packages


setup(
    name="weatherapp.accu",
    version="0.1.0",
    author="Vasyl Rostykus",
    description="AccuWeather provider",
    long_description="",
    packages=find_namespace_packages(),
    entry_points={
        'weatherapp.provider': 'accu=weatherapp.accu.provider:AccuProvider',
    },
    install_requires=[
        'requests',
        'bs4',
    ],
)
