"""
.. module:: app
.. moduleauthor:: Jared Patrick <jared.patrick@gmail.com>
"""

import tornado.web

from users.api import (
    SessionsResourceV1,
    UsersResourceV1
)


class Application(tornado.web.Application):
    handlers = [
        (r'^/sessions/?(?P<token>.*)/?', SessionsResourceV1,),
        (r'^/users/?', UsersResourceV1,)
    ]

    def __init__(self,
                 handlers=None,
                 default_host="",
                 transforms=None,
                 **settings):
        super().__init__(self.handlers, "", None, **settings)
