from setuptools import setup

setup(
    name='users',
    version='0.0.1',
    install_requires=[
        'bcrypt',
        'cerberus',
        'python-arango',
        'tornado',
        'raven',
    ],
    packages=[
        'users'
    ],
    scripts=[
        'bin/main'
    ]
)
