"""
.. module:: users
.. moduleauthor:: Jared Patrick <jared.patrick@gmail.com>
"""

import bcrypt
import pymysql.err

from users import exceptions


INSERT_USER = '''\
INSERT INTO `users`
    (`username`, `email`, `password`)
VALUES
    (%s, %s, %s);
'''

SELECT_USER_BY_ID = '''\
SELECT
    *
FROM
    `users`
WHERE
    id = %s;
'''

DELETE_USER = '''\
DELETE FROM
    `users`
WHERE
    id = %s;
'''

async def create(cursor, username, email, password):
    """Create a new user record in the database

    :param cursor: the mariadb database cursor
    :type: pymysql.cursors.DictCursor
    :param username: the user's unique user name
    :type username: str
    :param email: the user's email addres
    :type email: str
    :param password: the user's password
    :type password: str
    :return: the user record
    :rtype: dict
    """

    password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        user_id = cursor.execute(INSERT_USER, (username, email, password,))
        cursor.execute(SELECT_USER_BY_ID, (user_id,))
    except pymysql.err.IntegrityError:
        raise exceptions.UserExistsError()

    return cursor.fetchone()


async def read(cursor, user_id):
    """Fetch a user record from the database

    :param cursor: the mariadb database cursor
    :type: pymysql.cursors.DictCursor
    :param user_id: the id of the user
    :type user_id: int
    :return: the user record
    :rtype: dict
    """

    cursor.execute(SELECT_USER_BY_ID, (user_id,))
    user = cursor.fetchone()

    if user is None:
        raise exceptions.UserNotFoundError()

    return user

async def delete(cursor, user_id):
    """Delete a user record the database

    :param cursor: the mariadb database cursor
    :type: pymysql.cursors.DictCursor
    :param user_id: the id of the user
    :type user_id: int
    """

    cursor.execute(DELETE_USER, (user_id,))
