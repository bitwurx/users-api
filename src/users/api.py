"""
.. module:: api
.. moduleauthor:: Jared Patrick <jared.patrick@gmail.com>
"""

import json

import tornado.gen
import tornado.web

from users.exceptions import BadRequestError
from users.models import Session, User


def make_response(code=200, data=None):
    """Create a success response object

    :param code: the HTTP response code
    :type code: int
    :param data: the response data
    :type data: list or dict
    :return: the generated response object
    :rtype: dict
    """

    return {'code': code, 'status': 'success', 'data': data}


def parse_json_body(data):
    """JSON parse the body string

    :param data: the json body string
    :type data: string
    :raises: BadRequestError - if JSONDecodeError occurs
    :return: the decoded json string
    :rtype: dict
    """

    try:
        return json.loads(data)
    except Exception as e:
        raise BadRequestError(message=e.args[0], data='JSONDecodeError')


class SessionsResourceV1(tornado.web.RequestHandler):
    """Sessions REST API resource handler class
    """

    @tornado.gen.coroutine
    def get(self, token):
        """Get a user's session details
        """

        response = {}

        try:
            user = Session().read(token)
        except Exception as e:
            response = e.response()
        else:
            response = make_response(data=user)

        self.set_status(response['code'])
        self.write(response)


class UsersResourceV1(tornado.web.RequestHandler):
    """Users REST API resource handler class
    """

    schema = {'username': {'type': 'string'},
              'password': {'type': 'string'},
              'email': {'type': 'string'}}

    @tornado.gen.coroutine
    def post(self):
        """Create a new user account
        """

        response = {}

        try:
            body = parse_json_body(self.request.body.decode())
            user = User(**body).create()
            response = make_response(data=user)
        except Exception as e:
            response = e.response()

        self.set_status(response['code'])
        self.write(response)
