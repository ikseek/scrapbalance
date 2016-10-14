from setuptools import setup

setup(
    name='scrapbalance',
    version='0.1',
    packages=['scrapbalance'],
    url='',
    license='MIT',
    author='Igor Kozyrenko',
    author_email='igor@ikseek.com',
    description='Request mobile phone balance for Ukrainian mobile operators',
    entry_points={
        'console_scripts': ['scrapbalance=scrapbalance.cli:main'],
    },
    install_requires=['mechanicalsoup']
)
