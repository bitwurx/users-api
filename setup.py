from setuptools import setup

setup(
    name='users',
    version='0.0.1',
    install_requires=[
        'bcrypt',
        'pymysql',
        'sqlalchemy'
    ],
    packages=[
        'users'
    ],
    scripts=[
        'bin/main'
    ]
)
