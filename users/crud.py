"""
.. module:: users
.. moduleauthor:: Jared Patrick <jared.patrick@gmail.com>
"""

import bcrypt


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
    user_id = cursor.execute(INSERT_USER, (username, email, password,))
    cursor.execute(SELECT_USER_BY_ID, (user_id))

    return cursor.fetchone()
