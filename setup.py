from setuptools import setup

setup(
    name='users',
    version='0.0.1',
    install_requires=[
        'aiohttp',
        'bcrypt',
        'cchardet',
        'PyMySQL'
    ],
    packages=[
        'users'
    ],
    scripts=['bin/main']
)
