"""
.. module:: api
.. moduleauthor:: Jared Patrick <jared.patrick@gmail.com>
"""

import json
import os

import arango
import arango.exceptions

import bcrypt

import cerberus

import tornado.gen
import tornado.web


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


class UsersResourceV1(tornado.web.RequestHandler):
    schema = {
        'username': {'type': 'string'},
        'password': {'type': 'string'},
        'email': {'type': 'string'}
    }

    @tornado.gen.coroutine
    def post(self):
        """Create a new user document
        """

        global users

        body = json.loads(self.request.body.decode())
        body['password'] = bcrypt.hashpw(body['password'].encode(),
                                         bcrypt.gensalt())
        cerberus.Validator().validate(body, self.schema)
        users.insert({
            'username': body['username'],
            'password': body['password'],
            'email': body['email']
        })
