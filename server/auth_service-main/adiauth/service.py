#!/usr/bin/env python3

'''
    Implementacion del servicio de autenticacion
'''

import json
import logging
import secrets
from pathlib import Path

from adiauth import ADMIN, USER_TOKEN_SIZE, OWNER, DEFAULT_ENCODING
from adiauth.errors import Unauthorized, ObjectAlreadyExists, ObjectNotFound


_WRN = logging.warning


def _initialize_(db_file):
    '''Create an empty JSON file'''
    _WRN(f'Initializing new database in file "{db_file}"')
    with open(db_file, 'w', encoding=DEFAULT_ENCODING) as contents:
        json.dump({}, contents)


def _newToken_():
    '''Create a new token'''
    return secrets.token_urlsafe(USER_TOKEN_SIZE)


class AuthDB:
    '''
        Controla la base de datos persistente del servicio de autenticacion
    '''
    def __init__(self, db_file):
        if not Path(db_file).exists():
            _initialize_(db_file)
        self._db_file_ = db_file
        self.token_manager = None

        self._users_ = {}

        self._read_db_()

    def _read_db_(self):
        with open(self._db_file_, 'r', encoding=DEFAULT_ENCODING) as contents:
            self._users_ = json.load(contents)

    def _commit_(self):
        with open(self._db_file_, 'w', encoding=DEFAULT_ENCODING) as contents:
            json.dump(self._users_, contents, indent=2, sort_keys=True)

    def newUser(self, username, password_hash):
        '''Add new user to DB'''
        if (username == ADMIN) or (username in self._users_):
            raise ObjectAlreadyExists(f'User "{username}"')
        self._users_[username] = password_hash
        self._commit_()

    def removeUser(self, username):
        '''Remove user from DB'''
        if username not in self._users_:
            raise ObjectNotFound(f'User "{username}"')
        del self._users_[username]
        self._commit_()
        if isinstance(self.token_manager, TokenManager):
            try:
                self.token_manager.removeTokenOf(username)
            except ObjectNotFound: # pragma: no cover
                pass

    def changePasswordHash(self, username, new_password_hash):
        '''Change password hash of a given user'''
        if username not in self._users_:
            raise ObjectNotFound(f'User "{username}"')
        self._users_[username] = new_password_hash
        self._commit_()

    def exists(self, username):
        '''Return if a given user exists or not'''
        return username in [ADMIN] + list(self._users_.keys())

    def validHash(self, password_hash, username):
        '''Return if a given hash is valid or not'''
        if username == ADMIN and (self.token_manager is not None):
            return password_hash == self.token_manager.admin_token
        if username not in self._users_:
            return False
        return self._users_[username] == password_hash


class TokenManager:
    '''
        Controla la base de datos volatil del servicio de autenticacion
    '''
    def __init__(self, admin_token, authdb):
        self._admin_token_ = admin_token
        # Attach TokenManager() with AuthDB()
        self._authdb_ = authdb
        authdb.token_manager = self
        self._token_ = {}

    @property
    def admin_token(self):
        '''Return the admin token'''
        return self._admin_token_

    def newToken(self, username, password_hash):
        '''Create new token for a given username. Check credentials'''
        if not self._authdb_.validHash(password_hash, username):
            _WRN(f'Reject to create new token for user "{username}"')
            raise Unauthorized(username, 'Invalid password hash')

        token = _newToken_()
        self._token_[token] = { OWNER: username }
        return token

    def stop(self):
        '''Remove all tokens'''
        self._token_ = {}

    def removeTokenOf(self, user):
        '''Remove token for the given user (if exists)'''
        target_token = None
        for token, token_config in self._token_.items():
            if token_config[OWNER] == user:
                target_token = token
                break
        if target_token:
            self._remove_token_(target_token)

    def _remove_token_(self, token):
        '''Remove given token'''
        if token in self._token_:
            del self._token_[token]

    def ownerOf(self, token):
        '''Return the owner of a token or exception is token not exists'''
        if token not in self._token_:
            raise ObjectNotFound(f'Token #{token}')
        return self._token_[token][OWNER]
