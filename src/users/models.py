"""
.. module:: models
.. moduleauthor:: Jared Patrick <jared.patrick@gmail.com>
"""

import base64
import copy
import json
import os

import arango
import arango.exceptions
import bcrypt
import cerberus
import redis

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

    users.add_hash_index(fields=User.unique, unique=True)


class Session(object):
    """Session model class
    """

    schema = {'username': {'type': 'string', 'required': True},
              'password': {'type': 'string', 'required': True}}

    def __init__(self, **kwargs):
        """Session constructor method
        """

        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.token = kwargs.get('token')

    def create(self):
        """Create a new user session in redis

        :return: the created sessio ndetails
        :rtype: dict
        """

        global users

        try:
            user = list(users.find({'username': self.username}))[0]
        except IndexError:
            raise exceptions.NotFoundError('user')
        else:
            pwhash = user['password'].encode()
            if bcrypt.hashpw(self.password.encode(), pwhash) != pwhash:
                raise exceptions.BadRequestError(
                    'incorrect username or password',
                    'InvalidCredentialsError'
                )
            else:
                token = base64.b64encode(os.urandom(33))
                r = redis.Redis('redis', 6379)
                r.setex(token,
                        json.dumps({'user_id': user['_key']}),
                        3600)
                return {'token': token.decode()}

    def read(self):
        """Read the user details of a valid user session

        :return: the fetched user data
        :rtype: dict
        """

        global users

        r = redis.Redis('redis', 6379)

        try:
            token = r.get(self.token).decode()
        except AttributeError:
            raise exceptions.NotFoundError('session token')
        else:
            user_id = json.loads(token).get('user_id')
            user = users.get(user_id)
            del user['password']

        return user

    def update(self):
        """Update the user session extending the expiry
        """

        r = redis.Redis('redis', 6379)

        session = r.get(self.token)
        if session is None:
            raise exceptions.NotFoundError('session token')

        r.setex(self.token, session)

    def validate(self):
        """Validate the model instance data

        :raises: users.exceptions.BadRequestError if validate fails
        """

        document = {'username': self.username, 'password': self.password}
        validator = cerberus.Validator()

        if not validator.validate(document, self.schema):
            raise exceptions.BadRequestError(validator.errors,
                                             'ValidationError')


class User(object):
    """User model class
    """

    schema = {'username': {'type': 'string', 'required': True},
              'password': {'type': 'string', 'required': True},
              'email': {'type': 'string', 'required': True}}
    unique = ('username',)

    def __init__(self, **kwargs):
        """User constructor method
        """

        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.email = kwargs.get('email')

    def create(self):
        """Create the database resource record

        :raises: users.exceptions.ConflictError if username exists
        :return: the created user record
        :rtype: dict
        """

        global users

        self.validate()
        password = bcrypt.hashpw(self.password.encode(), bcrypt.gensalt())
        data = {'username': self.username,
                'password': password.decode(),
                'email': self.email}

        try:
            meta = users.insert(data)
        except arango.exceptions.DocumentInsertError:
            raise exceptions.ConflictError(fields=self.unique)
        else:
            user = copy.copy(data)
            user['id'] = meta['_key']
            del user['password']

            return user

    def validate(self):
        """Validate the model instance data

        :raises: users.exceptions.BadRequestError if validation fails
        """

        document = {'username': self.username,
                    'password': self.password,
                    'email': self.email}
        validator = cerberus.Validator()

        if not validator.validate(document, self.schema):
            raise exceptions.BadRequestError(validator.errors,
                                             'ValidationError')
