"""
.. module:: models
.. moduleauthor:: Jared Patrick <jared.patrick@gmail.com>
"""

import os
import time

import bcrypt

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(50))
    username = Column(String(50))
    password = Column(String(50))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.password = bcrypt.hashpw(kwargs['password'].encode(),
                                      bcrypt.gensalt())

    def __repr__(self):
        return '<User: %s, %s>' % (self.username, self.email)


def get_engine():
    host = 'mysql+pymysql://{user}:{pwd}@{host}/{db}'.format(
        user='root',
        pwd=os.environ.get('MYSQL_ROOT_PASSWORD'),
        host='mariadb',
        db=os.environ.get('MYSQL_DATABASE')
    )
    engine = create_engine(host)
    Base.metadata.create_all(engine)

    return engine
