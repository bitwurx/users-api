"""
.. module:: api
.. moduleauthor:: Jared Patrick <jared.patrick@gmail.com>
"""

import json

import tornado.gen
import tornado.web

from users.exceptions import BadRequestError
from users.models import User


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

        global users

        response = {}

        try:
            body = parse_json_body(self.request.body.decode())
            user = User(**body).create()
            response = make_response(data=user)
        except BadRequestError as e:
            response = e.response()

        self.write(json.dumps(response, indent=4))
