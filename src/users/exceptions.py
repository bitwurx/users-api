"""
.. module:: exceptions
.. moduleauthor:: Jared Patrick <jared.patrick@gmail.com>
"""


class BaseError(Exception):
    """Base request error exception class
    """

    def __init__(self, message, data):
        """BaseError construct method

        :param message: the verbose error message
        :type message: str
        :param data: the error name associated with the error
        :type data: str
        """

        self.message = message
        self.data = data

    def response(self):
        """Create the error HTTP response

        :return: the error response body
        :rtype: dict
        """

        return {'code': self.code,
                'status': 'error',
                'message': self.message,
                'data': self.data}


class BadRequestError(BaseError):
    """Bad request error exception class
    """

    code = 400
