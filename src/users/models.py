"""
.. module:: models
.. moduleauthor:: Jared Patrick <jared.patrick@gmail.com>
"""

import copy
import os

import arango
import bcrypt
import cerberus

from users import exceptions


users = None


def connect_arango():
    """Connect to the users collection in the arango database
    """

    global users

    client = arango.ArangoClient(
        protocol='http',
        host='arangodb',
        port=8529,
        username='root',
        password=os.environ['ARANGO_ROOT_PASSWORD'],
        enable_logging=True
    )

    try:
        db = client.create_database('alicia')
    except arango.exceptions.DatabaseCreateError:
        db = client.database('alicia')

    try:
        users = db.create_collection('users')
    except arango.exceptions.CollectionCreateError:
        users = db.collection('users')


class User(object):
    """User database model class
    """

    schema = {'username': {'type': 'string'},
              'password': {'type': 'string'},
              'email': {'type': 'string'}}

    def __init__(self, **kwargs):
        """User constructor method
        """

        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.email = kwargs.get('email')

    def create(self):
        """Create the database resource record
        """

        password = bcrypt.hashpw(self.password.encode(), bcrypt.gensalt())
        data = {'username': self.username,
                'password': password.decode(),
                'email': self.email}
        meta = users.insert(data)
        user = copy.copy(data)
        user['id'] = meta['_key']

        return user

    def validate(self):
        """Validate the model instance data
        """

        document = {'username': self.username,
                    'password': self.password,
                    'email': self.email}
        validator = cerberus.Validator()

        if not validator.validate(document, self.schema):
            raise exceptions.BadRequestError(validator.errors,
                                             'ValidationError')
