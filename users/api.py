"""
.. module:: api
.. moduleauthor:: Jared Patrick <jared.patrick@gmail.com>
"""

import os

import arango
import arango.exceptions


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
