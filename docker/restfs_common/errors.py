#!/usr/bin/env python3

'''RestFS errors'''


## Exit codes

NO_ERROR = 0
CMDCLI_ERROR = 1
CONNECTION_ERROR = 2
UNAUTHORIZED = 3

## Custom exceptions


class ConnectionError(Exception):
    '''Connection error'''
    def __init__(self, details=None):
        self._details_ = details

    def __str__(self):
        return 'Connection error' + ('' if self._details_ is None else f': {self._details_}')


class NotAttached(Exception):
    '''Not-Attached error'''
    def __str__(self):
        return 'Client not attached to a service access instance'


class Unauthorized(Exception):
    '''Authorization error'''
    def __init__(self, user='unknown', reason='unknown'):
        self._user_ = user
        self._reason_ = reason

    def __str__(self):
        return f'Authorization error for user "{self._user_}": {self._reason_}'


class ObjectNotFound(Exception):
    '''Object not found error'''
    def __init__(self, item='unknown'):
        self._item_ = item

    def __str__(self):
        return f'Requested item "{self._item_}" not found'


class ObjectAlreadyExists(Exception):
    '''Object already exists error'''
    def __init__(self, item='unknown'):
        self._item_ = item

    def __str__(self):
        return f'Trying to create already created item "{self._item_}"'


class UnexpectedError(Exception):
    '''Unknown/unexpected error'''
    def __init__(self, msg=None):
        self._msg_ = msg

    def __str__(self):
        return 'Unknown error' + (f': {self._msg_}' if self._msg_ is not None else '')


class AlreadyDoneError(Exception):
    '''Action already done'''
    def __init__(self, msg=None):
        self._msg_ = msg

    def __str__(self):
        return 'Requested action is already done' + (
            f': {self._msg_}' if self._msg_ is not None else ''
        )


class MissingMandatoryArgument(Exception):
    '''Some required argument is missing'''
    def __str__(self):
        return 'Mandatory argument is required but not provided'