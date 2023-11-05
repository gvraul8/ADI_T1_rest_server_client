#!/usr/bin/env python3

'''RestFS errors'''


## Exit codes

NO_ERROR = 0
CMDCLI_ERROR = 1
CONNECTION_ERROR = 2
UNAUTHORIZED = 3

## Custom exceptions

class InvalidBlob(Exception):
    '''Invalid blob'''
    def __init__(self, blob='unknown'):
        self._item_ = blob

    def __str__(self):
        return f'Invalid blob "{self._item_}"'

class Unauthorized(Exception):
    '''Authorization error'''
    def __init__(self, user='unknown', reason='unknown'):
        self._user_ = user
        self._reason_ = reason

    def __str__(self):
        return f'Authorization error for user "{self._user_}": {self._reason_}'


class BlobServiceError(Exception):
    '''BlobServiceError'''
    def __init__(self, blob='unknown'):
        self._item_ = blob

    def __str__(self):
        return f'Requested blob "{self._item_}" not found'
