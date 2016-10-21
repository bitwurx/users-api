"""
.. module:: resources
.. moduleauthor:: Jared Patrick <jared.patrick@gmail.com>
"""

from sqlalchemy.orm import sessionmaker

from users.models import get_engine


class UsersResource(object):
    def __init__(self):
        self.session = sessionmaker(bind=get_engine())()

    def on_get(self, request, response):
        pass
