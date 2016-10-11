"""
.. module:: exceptions
-- moduleauthor:: Jared Patrick <jared.patrick@gmail.com>
"""


class UserExistsError(Exception):
    """User exists exception class
    """

    def __init__(self):
        self.args = ('provided username already exists',)


class UserNotFoundError(Exception):
    """User not found exception class
    """

    def __init__(self):
        self.args = ('provided user id does not exist',)
