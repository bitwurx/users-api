"""
.. module:: api
.. moduleauthor:: Jared Patrick <jared.patrick@gmail.com>
"""

import falcon

from users.resources import (
    UsersResource
)

api = falcon.API()
api.add_route('/users', UsersResource())
